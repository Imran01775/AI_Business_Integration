"""Identity application facade."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from app.core.auth.jwt_service import JwtService
from app.core.auth.password_hasher import Argon2PasswordHasher
from app.core.auth.secure_token import generate_opaque_token, hash_token
from app.core.clock import Clock
from app.core.config import AppConfig
from app.core.db.uow import UnitOfWork
from app.core.email.ports import EmailMessage, EmailSenderPort
from app.core.ids import IdGenerator
from app.modules.audit.application.ports import AuditPort
from app.modules.identity.application.dto import AuthResult, SessionView
from app.modules.identity.domain.errors import EmailNotVerifiedError
from app.modules.identity.infrastructure.repositories import SqlIdentityRepository
from app.modules.settings.application.templates import TemplateRenderer
from app.shared.context import SettingsResolveContext
from app.shared.events import ActorRef, DomainEvent


class IdentityFacade:
    def __init__(
        self,
        *,
        config: AppConfig,
        repo: SqlIdentityRepository,
        uow: UnitOfWork,
        jwt: JwtService,
        hasher: Argon2PasswordHasher,
        clock: Clock,
        ids: IdGenerator,
        email: EmailSenderPort,
        templates: TemplateRenderer,
        audit: AuditPort,
    ) -> None:
        self._config = config
        self._repo = repo
        self._uow = uow
        self._jwt = jwt
        self._hasher = hasher
        self._clock = clock
        self._ids = ids
        self._email = email
        self._templates = templates
        self._audit = audit

    def _refresh_expiry(self) -> datetime:
        return self._clock.now() + timedelta(days=self._config.jwt_refresh_token_ttl_days)

    async def register(
        self,
        *,
        email: str,
        password: str,
        display_name: str,
        locale: str,
        trace_id: str,
    ) -> UUID:
        password_hash = self._hasher.hash(password)
        async with self._uow:
            user = await self._repo.create_user(
                email=email.lower().strip(),
                display_name=display_name,
                password_hash=password_hash,
                locale=locale,
                session=self._uow.session,
            )
            raw_token = generate_opaque_token()
            await self._repo.create_email_verification(
                user.id,
                raw_token,
                self._clock.now() + timedelta(hours=24),
                self._uow.session,
            )
            verify_url = f"{self._config.app_public_url}/verify-email?token={raw_token}"
            body = await self._templates.render(
                "identity.verify_email",
                SettingsResolveContext(),
                {"verify_url": verify_url},
                locale=locale,
            )
            await self._email.send(
                EmailMessage(to=email, subject="Verify your email", body_text=body),
            )
            event = DomainEvent(
                event_id=self._ids.uuid7(),
                type="identity.user.registered",
                occurred_at=self._clock.now(),
                tenant_id=None,
                trace_id=trace_id,
                actor=ActorRef(type="user", id=str(user.id)),
                payload={"user_id": str(user.id), "email": email},
            )
            self._uow.collect_event(event)
            await self._audit.record(
                action="identity.user.registered",
                entity_type="user",
                entity_id=str(user.id),
                tenant_id=None,
                actor_id=str(user.id),
                before=None,
                after={"email": email},
                trace_id=trace_id,
                session=self._uow.session,
            )
            return user.id

    async def verify_email(self, token: str, trace_id: str) -> UUID:
        user = await self._repo.consume_email_verification(token)
        await self._audit.record(
            action="identity.email.verified",
            entity_type="user",
            entity_id=str(user.id),
            tenant_id=None,
            actor_id=str(user.id),
            before=None,
            after=None,
            trace_id=trace_id,
            session=None,
        )
        return user.id

    async def login(
        self,
        *,
        email: str,
        password: str,
        client_type: Literal["web", "mobile"],
        device_name: str | None,
        ip_address: str | None,
        user_agent: str | None,
        trace_id: str,
    ) -> AuthResult:
        user = await self._repo.verify_password(email.lower().strip(), password, self._hasher)
        if user.email_verified_at is None:
            raise EmailNotVerifiedError()
        active = await self._repo.count_active_sessions(user.id)
        if active >= self._config.auth_max_sessions:
            await self._repo.revoke_all_sessions(user.id)
        csrf_raw: str | None = None
        csrf_hash: str | None = None
        if client_type == "web":
            csrf_raw = generate_opaque_token(24)
            csrf_hash = hash_token(csrf_raw)
        async with self._uow:
            device = await self._repo.create_session(
                user_id=user.id,
                client_type=client_type,
                device_name=device_name,
                ip_address=ip_address,
                user_agent=user_agent,
                csrf_token_hash=csrf_hash,
                session=self._uow.session,
            )
            family_id = self._ids.uuid7()
            refresh_raw = generate_opaque_token()
            await self._repo.issue_refresh_token(
                session_id=device.id,
                user_id=user.id,
                family_id=family_id,
                raw_token=refresh_raw,
                expires_at=self._refresh_expiry(),
                session=self._uow.session,
            )
            platform_roles = await self._repo.list_platform_roles(user.id)
            access = self._jwt.encode_access_token(
                user_id=user.id,
                session_id=device.id,
                token_version=user.token_version,
                platform_roles=platform_roles,
            )
            await self._audit.record(
                action="identity.login",
                entity_type="device_session",
                entity_id=str(device.id),
                tenant_id=None,
                actor_id=str(user.id),
                before=None,
                after={"client_type": client_type},
                trace_id=trace_id,
                session=self._uow.session,
            )
            return AuthResult(
                access_token=access,
                refresh_token=refresh_raw,
                csrf_token=csrf_raw,
                user_id=user.id,
                session_id=device.id,
            )

    async def refresh(self, refresh_token: str, trace_id: str) -> AuthResult:
        new_raw = generate_opaque_token()
        row, device, user = await self._repo.rotate_refresh_token(
            refresh_token,
            new_raw,
            self._refresh_expiry(),
        )
        platform_roles = await self._repo.list_platform_roles(user.id)
        access = self._jwt.encode_access_token(
            user_id=user.id,
            session_id=device.id,
            token_version=user.token_version,
            platform_roles=platform_roles,
        )
        await self._audit.record(
            action="identity.token.refreshed",
            entity_type="device_session",
            entity_id=str(device.id),
            tenant_id=None,
            actor_id=str(user.id),
            before=None,
            after=None,
            trace_id=trace_id,
            session=None,
        )
        return AuthResult(
            access_token=access,
            refresh_token=new_raw,
            csrf_token=None,
            user_id=user.id,
            session_id=device.id,
        )

    async def logout(self, user_id: UUID, session_id: UUID, trace_id: str, all_sessions: bool) -> None:
        if all_sessions:
            await self._repo.revoke_all_sessions(user_id)
        else:
            await self._repo.revoke_session(user_id, session_id)
        await self._audit.record(
            action="identity.logout",
            entity_type="device_session",
            entity_id=str(session_id),
            tenant_id=None,
            actor_id=str(user_id),
            before=None,
            after={"all_sessions": all_sessions},
            trace_id=trace_id,
            session=None,
        )

    async def request_password_reset(self, email: str, locale: str) -> None:
        user = await self._repo.get_user_by_email(email.lower().strip())
        if user is None:
            return
        raw = generate_opaque_token()
        await self._repo.create_password_reset(user.id, raw, self._clock.now() + timedelta(hours=1))
        reset_url = f"{self._config.app_public_url}/reset-password?token={raw}"
        body = await self._templates.render(
            "identity.reset_password",
            SettingsResolveContext(),
            {"reset_url": reset_url},
            locale=locale,
        )
        await self._email.send(
            EmailMessage(to=email, subject="Reset your password", body_text=body),
        )

    async def reset_password(self, token: str, new_password: str, trace_id: str) -> None:
        password_hash = self._hasher.hash(new_password)
        user = await self._repo.reset_password(token, password_hash)
        await self._repo.revoke_all_sessions(user.id)
        await self._audit.record(
            action="identity.password.reset",
            entity_type="user",
            entity_id=str(user.id),
            tenant_id=None,
            actor_id=str(user.id),
            before=None,
            after=None,
            trace_id=trace_id,
            session=None,
        )

    async def revoke_session(self, user_id: UUID, session_id: UUID, trace_id: str) -> None:
        await self._repo.revoke_session(user_id, session_id)
        await self._audit.record(
            action="identity.session.revoked",
            entity_type="device_session",
            entity_id=str(session_id),
            tenant_id=None,
            actor_id=str(user_id),
            before=None,
            after=None,
            trace_id=trace_id,
            session=None,
        )

    async def list_sessions(self, user_id: UUID, current_session_id: UUID) -> list[SessionView]:
        rows = await self._repo.list_sessions(user_id, current_session_id)
        return [
            SessionView(
                id=r.id,
                client_type=r.client_type,
                device_name=r.device_name,
                ip_address=r.ip_address,
                last_seen_at=r.last_seen_at,
                created_at=r.created_at,
                is_current=r.id == current_session_id,
            )
            for r in rows
        ]

    async def validate_access_token_session(self, user_id: UUID, session_id: UUID, token_version: int) -> None:
        user = await self._repo.get_user(user_id)
        device = await self._repo.get_session(session_id)
        if user is None or device is None or device.user_id != user_id:
            from app.core.errors.exceptions import UnauthenticatedError

            raise UnauthenticatedError()
        if device.revoked_at is not None or user.token_version != token_version:
            from app.core.errors.exceptions import UnauthenticatedError

            raise UnauthenticatedError()

    async def get_platform_roles(self, user_id: UUID) -> list[str]:
        return await self._repo.list_platform_roles(user_id)

    async def get_user_email(self, user_id: UUID) -> str:
        user = await self._repo.get_user(user_id)
        if user is None:
            from app.core.errors.exceptions import NotFoundError

            raise NotFoundError()
        return str(user.email)

    async def session_csrf_hash(self, session_id: UUID) -> str | None:
        device = await self._repo.get_session(session_id)
        return device.csrf_token_hash if device else None

    async def seed_super_admin(self, email: str, password: str, display_name: str) -> UUID:
        normalized = email.lower().strip()
        existing = await self._repo.get_user_by_email(normalized)
        if existing is not None:
            await self._repo.assign_platform_role(existing.id, "super_admin")
            return existing.id
        password_hash = self._hasher.hash(password)
        async with self._uow:
            user = await self._repo.create_user(
                email=normalized,
                display_name=display_name,
                password_hash=password_hash,
                locale="en",
                session=self._uow.session,
            )
            user.email_verified_at = datetime.now(UTC)
            await self._repo.assign_platform_role(
                user.id,
                "super_admin",
                session=self._uow.session,
            )
            return user.id
