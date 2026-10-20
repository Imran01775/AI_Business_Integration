"""SQL identity persistence."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.auth.secure_token import hash_token
from app.core.db.session import session_scope
from app.core.db.session_context import apply_user_context
from app.core.ids import IdGenerator
from app.modules.identity.domain.errors import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    InvalidVerificationTokenError,
    RefreshTokenReuseError,
    SessionNotFoundError,
)
from app.modules.identity.infrastructure.models import (
    Credential,
    DeviceSession,
    EmailVerification,
    PasswordReset,
    PlatformRoleAssignment,
    RefreshToken,
    User,
)


class SqlIdentityRepository:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def create_user(
        self,
        *,
        email: str,
        display_name: str,
        password_hash: str,
        locale: str,
        session: AsyncSession | None = None,
    ) -> User:
        async def _run(sess: AsyncSession) -> User:
            existing = await sess.scalar(select(User).where(User.email == email))
            if existing is not None:
                raise EmailAlreadyRegisteredError()
            user = User(
                id=self._ids.uuid7(),
                email=email,
                display_name=display_name,
                locale=locale,
            )
            sess.add(user)
            sess.add(Credential(user_id=user.id, password_hash=password_hash, updated_at=datetime.now(UTC)))
            await sess.flush()
            return user

        if session is not None:
            return await _run(session)
        async with session_scope(self._session_factory) as sess:
            return await _run(sess)

    async def get_user_by_email(self, email: str) -> User | None:
        async with session_scope(self._session_factory) as sess:
            return await sess.scalar(select(User).where(User.email == email))

    async def get_user(self, user_id: UUID) -> User | None:
        async with session_scope(self._session_factory) as sess:
            return await sess.get(User, user_id)

    async def verify_password(self, email: str, password: str, hasher: object) -> User:
        async with session_scope(self._session_factory) as sess:
            user = await sess.scalar(select(User).where(User.email == email))
            if user is None:
                raise InvalidCredentialsError()
            cred = await sess.get(Credential, user.id)
            if cred is None or not hasher.verify(cred.password_hash, password):  # type: ignore[attr-defined]
                raise InvalidCredentialsError()
            return user

    async def create_email_verification(
        self,
        user_id: UUID,
        raw_token: str,
        expires_at: datetime,
        session: AsyncSession,
    ) -> None:
        session.add(
            EmailVerification(
                id=self._ids.uuid7(),
                user_id=user_id,
                token_hash=hash_token(raw_token),
                expires_at=expires_at,
                created_at=datetime.now(UTC),
            )
        )

    async def consume_email_verification(self, raw_token: str) -> User:
        async with session_scope(self._session_factory) as sess:
            row = await sess.scalar(
                select(EmailVerification).where(EmailVerification.token_hash == hash_token(raw_token))
            )
            now = datetime.now(UTC)
            if row is None or row.consumed_at is not None or row.expires_at < now:
                raise InvalidVerificationTokenError()
            user = await sess.get(User, row.user_id)
            if user is None:
                raise InvalidVerificationTokenError()
            user.email_verified_at = now
            row.consumed_at = now
            await sess.flush()
            return user

    async def create_password_reset(self, user_id: UUID, raw_token: str, expires_at: datetime) -> None:
        async with session_scope(self._session_factory) as sess:
            sess.add(
                PasswordReset(
                    id=self._ids.uuid7(),
                    user_id=user_id,
                    token_hash=hash_token(raw_token),
                    expires_at=expires_at,
                    created_at=datetime.now(UTC),
                )
            )

    async def reset_password(self, raw_token: str, password_hash: str) -> User:
        async with session_scope(self._session_factory) as sess:
            row = await sess.scalar(
                select(PasswordReset).where(PasswordReset.token_hash == hash_token(raw_token))
            )
            now = datetime.now(UTC)
            if row is None or row.consumed_at is not None or row.expires_at < now:
                raise InvalidResetTokenError()
            user = await sess.get(User, row.user_id)
            if user is None:
                raise InvalidResetTokenError()
            cred = await sess.get(Credential, user.id)
            if cred is None:
                raise InvalidResetTokenError()
            cred.password_hash = password_hash
            cred.updated_at = now
            user.token_version += 1
            row.consumed_at = now
            await sess.flush()
            return user

    async def create_session(
        self,
        *,
        user_id: UUID,
        client_type: str,
        device_name: str | None,
        ip_address: str | None,
        user_agent: str | None,
        csrf_token_hash: str | None,
        session: AsyncSession,
    ) -> DeviceSession:
        now = datetime.now(UTC)
        device = DeviceSession(
            id=self._ids.uuid7(),
            user_id=user_id,
            client_type=client_type,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            csrf_token_hash=csrf_token_hash,
            last_seen_at=now,
            created_at=now,
        )
        session.add(device)
        await session.flush()
        return device

    async def issue_refresh_token(
        self,
        *,
        session_id: UUID,
        user_id: UUID,
        family_id: UUID,
        raw_token: str,
        expires_at: datetime,
        session: AsyncSession,
    ) -> RefreshToken:
        row = RefreshToken(
            id=self._ids.uuid7(),
            session_id=session_id,
            user_id=user_id,
            family_id=family_id,
            token_hash=hash_token(raw_token),
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )
        session.add(row)
        await session.flush()
        return row

    async def rotate_refresh_token(
        self,
        raw_token: str,
        new_raw_token: str,
        new_expires_at: datetime,
    ) -> tuple[RefreshToken, DeviceSession, User]:
        async with session_scope(self._session_factory) as sess:
            token_hash = hash_token(raw_token)
            row = await sess.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
            now = datetime.now(UTC)
            if row is None:
                raise InvalidCredentialsError()
            if row.revoked_at is not None and row.replaced_by_id is not None:
                await self._revoke_family(sess, row.family_id)
                raise RefreshTokenReuseError()
            if row.expires_at < now or row.revoked_at is not None:
                raise InvalidCredentialsError()
            device = await sess.get(DeviceSession, row.session_id)
            user = await sess.get(User, row.user_id)
            if device is None or user is None or device.revoked_at is not None:
                raise InvalidCredentialsError()
            new_row = RefreshToken(
                id=self._ids.uuid7(),
                session_id=row.session_id,
                user_id=row.user_id,
                family_id=row.family_id,
                token_hash=hash_token(new_raw_token),
                expires_at=new_expires_at,
                created_at=now,
            )
            sess.add(new_row)
            await sess.flush()
            row.replaced_by_id = new_row.id
            row.revoked_at = now
            device.last_seen_at = now
            await sess.flush()
            return new_row, device, user

    async def _revoke_family(self, sess: AsyncSession, family_id: UUID) -> None:
        now = datetime.now(UTC)
        await sess.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id)
            .values(revoked_at=now)
        )
        session_ids = (
            await sess.scalars(select(RefreshToken.session_id).where(RefreshToken.family_id == family_id))
        ).all()
        if session_ids:
            await sess.execute(
                update(DeviceSession)
                .where(DeviceSession.id.in_(session_ids))
                .values(revoked_at=now)
            )

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> None:
        async with session_scope(self._session_factory) as sess:
            await apply_user_context(sess, user_id)
            device = await sess.get(DeviceSession, session_id)
            if device is None or device.user_id != user_id:
                raise SessionNotFoundError()
            now = datetime.now(UTC)
            device.revoked_at = now
            await sess.execute(
                update(RefreshToken)
                .where(RefreshToken.session_id == session_id)
                .values(revoked_at=now)
            )

    async def revoke_all_sessions(self, user_id: UUID, except_session_id: UUID | None = None) -> None:
        async with session_scope(self._session_factory) as sess:
            await apply_user_context(sess, user_id)
            now = datetime.now(UTC)
            stmt = update(DeviceSession).where(DeviceSession.user_id == user_id).values(revoked_at=now)
            if except_session_id is not None:
                stmt = stmt.where(DeviceSession.id != except_session_id)
            await sess.execute(stmt)

    async def list_sessions(self, user_id: UUID, current_session_id: UUID) -> list[DeviceSession]:
        async with session_scope(self._session_factory) as sess:
            await apply_user_context(sess, user_id)
            result = await sess.scalars(
                select(DeviceSession)
                .where(DeviceSession.user_id == user_id, DeviceSession.revoked_at.is_(None))
                .order_by(DeviceSession.last_seen_at.desc())
            )
            return list(result.all())

    async def get_session(self, session_id: UUID) -> DeviceSession | None:
        async with session_scope(self._session_factory) as sess:
            return await sess.get(DeviceSession, session_id)

    async def count_active_sessions(self, user_id: UUID) -> int:
        async with session_scope(self._session_factory) as sess:
            await apply_user_context(sess, user_id)
            count = await sess.scalar(
                select(func.count())
                .select_from(DeviceSession)
                .where(DeviceSession.user_id == user_id, DeviceSession.revoked_at.is_(None))
            )
            return int(count or 0)

    async def list_platform_roles(self, user_id: UUID) -> list[str]:
        async with session_scope(self._session_factory) as sess:
            roles = await sess.scalars(
                select(PlatformRoleAssignment.role).where(PlatformRoleAssignment.user_id == user_id)
            )
            return list(roles.all())

    async def assign_platform_role(
        self,
        user_id: UUID,
        role: str,
        *,
        session: AsyncSession | None = None,
    ) -> None:
        async def _run(sess: AsyncSession) -> None:
            existing = await sess.scalar(
                select(PlatformRoleAssignment).where(
                    PlatformRoleAssignment.user_id == user_id,
                    PlatformRoleAssignment.role == role,
                )
            )
            if existing is None:
                sess.add(
                    PlatformRoleAssignment(
                        id=self._ids.uuid7(),
                        user_id=user_id,
                        role=role,
                        created_at=datetime.now(UTC),
                    )
                )

        if session is not None:
            await _run(session)
            return
        async with session_scope(self._session_factory) as sess:
            await _run(sess)

    async def get_user_token_version(self, user_id: UUID) -> int:
        async with session_scope(self._session_factory) as sess:
            user = await sess.get(User, user_id)
            if user is None:
                raise InvalidCredentialsError()
            return user.token_version
