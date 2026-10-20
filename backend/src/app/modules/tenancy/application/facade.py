"""Tenancy application facade."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from app.core.clock import Clock
from app.core.config import AppConfig
from app.core.db.uow import UnitOfWork
from app.core.email.ports import EmailMessage, EmailSenderPort
from app.core.ids import IdGenerator
from app.modules.audit.application.ports import AuditPort
from app.modules.settings.application.templates import TemplateRenderer
from app.modules.tenancy.infrastructure.repositories import TenancyRepository
from app.shared.context import SettingsResolveContext
from app.shared.events import ActorRef, DomainEvent


class TenancyFacade:
    def __init__(
        self,
        *,
        config: AppConfig,
        repo: TenancyRepository,
        uow: UnitOfWork,
        clock: Clock,
        ids: IdGenerator,
        email: EmailSenderPort,
        templates: TemplateRenderer,
        audit: AuditPort,
    ) -> None:
        self._config = config
        self._repo = repo
        self._uow = uow
        self._clock = clock
        self._ids = ids
        self._email = email
        self._templates = templates
        self._audit = audit

    async def create_tenant(
        self,
        *,
        owner_user_id: UUID,
        display_name: str,
        slug: str | None,
        timezone: str,
        locale: str,
        currency: str,
        trace_id: str,
    ) -> UUID:
        async with self._uow:
            tenant = await self._repo.create_tenant(
                display_name=display_name,
                slug=slug,
                timezone=timezone,
                locale=locale,
                currency=currency,
                owner_user_id=owner_user_id,
                session=self._uow.session,
            )
            event = DomainEvent(
                event_id=self._ids.uuid7(),
                type="tenancy.tenant.created",
                occurred_at=self._clock.now(),
                tenant_id=tenant.id,
                trace_id=trace_id,
                actor=ActorRef(type="user", id=str(owner_user_id)),
                payload={"tenant_id": str(tenant.id), "slug": tenant.slug},
            )
            self._uow.collect_event(event)
            await self._audit.record(
                action="tenancy.tenant.created",
                entity_type="tenant",
                entity_id=str(tenant.id),
                tenant_id=str(tenant.id),
                actor_id=str(owner_user_id),
                before=None,
                after={"slug": tenant.slug},
                trace_id=trace_id,
                session=self._uow.session,
            )
            return tenant.id

    async def invite_member(
        self,
        *,
        tenant_id: UUID,
        email: str,
        role: str,
        invited_by: UUID,
        locale: str,
        trace_id: str,
    ) -> None:
        from app.core.auth.secure_token import generate_opaque_token

        raw = generate_opaque_token()
        async with self._uow:
            await self._repo.create_invitation(
                tenant_id=tenant_id,
                email=email,
                role=role,
                invited_by=invited_by,
                raw_token=raw,
                expires_at=self._clock.now() + timedelta(days=7),
                session=self._uow.session,
            )
            tenant = await self._repo.get_tenant(tenant_id)
            business_name = tenant.display_name if tenant else "Business"
            accept_url = f"{self._config.app_public_url}/accept-invite?token={raw}"
            body = await self._templates.render(
                "tenancy.invitation",
                SettingsResolveContext(tenant_id=tenant_id),
                {"business_name": business_name, "accept_url": accept_url},
                locale=locale,
            )
            await self._email.send(
                EmailMessage(to=email, subject="Team invitation", body_text=body),
            )
            await self._audit.record(
                action="tenancy.invitation.sent",
                entity_type="invitation",
                entity_id=email,
                tenant_id=str(tenant_id),
                actor_id=str(invited_by),
                before=None,
                after={"role": role},
                trace_id=trace_id,
                session=self._uow.session,
            )

    async def accept_invitation(self, token: str, user_id: UUID, user_email: str, trace_id: str) -> UUID:
        async with self._uow:
            membership = await self._repo.accept_invitation(
                token,
                user_id,
                user_email,
                session=self._uow.session,
            )
            event = DomainEvent(
                event_id=self._ids.uuid7(),
                type="tenancy.member.added",
                occurred_at=self._clock.now(),
                tenant_id=membership.tenant_id,
                trace_id=trace_id,
                actor=ActorRef(type="user", id=str(user_id)),
                payload={
                    "tenant_id": str(membership.tenant_id),
                    "user_id": str(user_id),
                    "role": membership.role,
                },
            )
            self._uow.collect_event(event)
        await self._audit.record(
            action="tenancy.member.added",
            entity_type="membership",
            entity_id=str(membership.id),
            tenant_id=str(membership.tenant_id),
            actor_id=str(user_id),
            before=None,
            after={"role": membership.role},
            trace_id=trace_id,
            session=None,
        )
        return membership.tenant_id
