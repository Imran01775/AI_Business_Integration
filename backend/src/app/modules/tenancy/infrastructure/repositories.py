"""Tenancy SQL repositories."""

from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.auth.secure_token import hash_token
from app.core.db.session import session_scope
from app.core.db.session_context import apply_user_context
from app.core.db.tenant import TenantContext
from app.core.errors.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.core.ids import IdGenerator
from app.modules.tenancy.infrastructure.models import (
    Invitation,
    Membership,
    OnboardingState,
    Tenant,
)


def slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:48] or "business"
    return base


class TenancyRepository:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def create_tenant(
        self,
        *,
        display_name: str,
        slug: str | None,
        timezone: str,
        locale: str,
        currency: str,
        owner_user_id: UUID,
        session: AsyncSession,
    ) -> Tenant:
        chosen = slug or slugify(display_name)
        existing = await session.scalar(select(Tenant).where(Tenant.slug == chosen))
        if existing is not None:
            chosen = f"{chosen}-{self._ids.uuid7().hex[:6]}"
        tenant = Tenant(
            id=self._ids.uuid7(),
            slug=chosen,
            display_name=display_name,
            timezone=timezone,
            locale=locale,
            currency=currency,
        )
        session.add(tenant)
        await session.flush()
        await TenantContext(tenant_id=tenant.id).apply(session)
        session.add(
            Membership(
                id=self._ids.uuid7(),
                tenant_id=tenant.id,
                user_id=owner_user_id,
                role="owner",
            )
        )
        session.add(
            OnboardingState(
                tenant_id=tenant.id,
                step="created",
                payload={},
                updated_at=datetime.now(),
            )
        )
        await session.flush()
        return tenant

    async def get_membership(self, tenant_id: UUID, user_id: UUID) -> Membership | None:
        async with session_scope(self._session_factory) as session:
            await apply_user_context(session, user_id)
            await TenantContext(tenant_id=tenant_id).apply(session)
            return await session.scalar(
                select(Membership).where(
                    Membership.tenant_id == tenant_id,
                    Membership.user_id == user_id,
                )
            )

    async def list_memberships_for_user(self, user_id: UUID) -> list[tuple[Membership, Tenant]]:
        async with session_scope(self._session_factory) as session:
            await apply_user_context(session, user_id)
            rows = await session.execute(
                select(Membership, Tenant)
                .join(Tenant, Tenant.id == Membership.tenant_id)
                .where(Membership.user_id == user_id)
            )
            return list(rows.all())

    async def create_invitation(
        self,
        *,
        tenant_id: UUID,
        email: str,
        role: str,
        invited_by: UUID,
        raw_token: str,
        expires_at: datetime,
        session: AsyncSession,
    ) -> Invitation:
        await TenantContext(tenant_id=tenant_id).apply(session)
        inv = Invitation(
            id=self._ids.uuid7(),
            tenant_id=tenant_id,
            email=email.lower().strip(),
            role=role,
            token_hash=hash_token(raw_token),
            invited_by_user_id=invited_by,
            expires_at=expires_at,
            created_at=datetime.now(),
        )
        session.add(inv)
        await session.flush()
        return inv

    async def accept_invitation(
        self,
        raw_token: str,
        user_id: UUID,
        user_email: str,
        *,
        session: AsyncSession | None = None,
    ) -> Membership:
        async def _run(sess: AsyncSession) -> Membership:
            inv = await sess.scalar(
                select(Invitation).where(Invitation.token_hash == hash_token(raw_token))
            )
            now = datetime.now()
            if inv is None or inv.revoked_at is not None or inv.accepted_at is not None:
                raise NotFoundError(details={"reason": "invitation"})
            if inv.expires_at < now:
                raise ConflictError(details={"reason": "expired"})
            if inv.email.lower() != user_email.lower():
                raise PermissionDeniedError(details={"reason": "email_mismatch"})
            await TenantContext(tenant_id=inv.tenant_id).apply(sess)
            existing = await sess.scalar(
                select(Membership).where(
                    Membership.tenant_id == inv.tenant_id,
                    Membership.user_id == user_id,
                )
            )
            if existing is not None:
                raise ConflictError(details={"reason": "already_member"})
            membership = Membership(
                id=self._ids.uuid7(),
                tenant_id=inv.tenant_id,
                user_id=user_id,
                role=inv.role,
            )
            sess.add(membership)
            inv.accepted_at = now
            await sess.flush()
            return membership

        if session is not None:
            return await _run(session)
        async with session_scope(self._session_factory) as sess:
            return await _run(sess)

    async def change_role(
        self,
        tenant_id: UUID,
        target_user_id: UUID,
        new_role: str,
        actor_user_id: UUID,
    ) -> Membership:
        async with session_scope(self._session_factory) as session:
            await apply_user_context(session, actor_user_id)
            await TenantContext(tenant_id=tenant_id).apply(session)
            membership = await session.scalar(
                select(Membership).where(
                    Membership.tenant_id == tenant_id,
                    Membership.user_id == target_user_id,
                )
            )
            if membership is None:
                raise NotFoundError()
            membership.role = new_role
            await session.flush()
            return membership

    async def remove_member(self, tenant_id: UUID, target_user_id: UUID, actor_user_id: UUID) -> None:
        async with session_scope(self._session_factory) as session:
            await apply_user_context(session, actor_user_id)
            await TenantContext(tenant_id=tenant_id).apply(session)
            membership = await session.scalar(
                select(Membership).where(
                    Membership.tenant_id == tenant_id,
                    Membership.user_id == target_user_id,
                )
            )
            if membership is None:
                raise NotFoundError()
            if membership.role == "owner":
                raise PermissionDeniedError(details={"reason": "cannot_remove_owner"})
            await session.delete(membership)

    async def get_tenant(self, tenant_id: UUID) -> Tenant | None:
        async with session_scope(self._session_factory) as session:
            return await session.get(Tenant, tenant_id)
