"""Tenant persistence helpers."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.session import session_scope
from app.core.ids import IdGenerator
from app.modules.tenancy.infrastructure.models import Tenant


class TenantRepository:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def create(self, slug: str, display_name: str) -> Tenant:
        async with session_scope(self._session_factory) as session:
            tenant = Tenant(
                id=self._ids.uuid7(),
                slug=slug,
                display_name=display_name,
            )
            session.add(tenant)
            await session.flush()
            return tenant

    async def get(self, tenant_id: UUID) -> Tenant | None:
        async with session_scope(self._session_factory) as session:
            return await session.get(Tenant, tenant_id)

    async def get_by_slug(self, slug: str) -> Tenant | None:
        async with session_scope(self._session_factory) as session:
            stmt = select(Tenant).where(Tenant.slug == slug)
            return (await session.execute(stmt)).scalar_one_or_none()
