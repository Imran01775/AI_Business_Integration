"""Reusable tenant-isolation helpers (R-TEN-05)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.tenant import TenantContext
from app.modules.tenancy.infrastructure.repository import TenantRepository


async def create_test_tenants(
    repo: TenantRepository,
    *,
    slug_a: str = "tenant-a",
    slug_b: str = "tenant-b",
) -> tuple[UUID, UUID]:
    tenant_a = await repo.create(slug_a, "Tenant A")
    tenant_b = await repo.create(slug_b, "Tenant B")
    return tenant_a.id, tenant_b.id


async def assert_tenant_cannot_read_row(
    session_factory: async_sessionmaker[AsyncSession],
    tenant_id: UUID,
    sql: str,
    params: dict[str, object],
) -> None:
    async with session_factory() as session:
        await TenantContext(tenant_id=tenant_id).apply(session)
        result = await session.execute(text(sql), params)
        assert result.first() is None


async def run_cross_tenant_check(
    session_factory: async_sessionmaker[AsyncSession],
    owner_tenant_id: UUID,
    other_tenant_id: UUID,
    insert_fn: Callable[[AsyncSession, UUID], Awaitable[UUID]],
    select_sql: str,
    id_param: str = "row_id",
) -> None:
    """Insert as owner tenant; other tenant must not see the row under RLS."""
    async with session_factory() as session:
        await TenantContext(tenant_id=owner_tenant_id).apply(session)
        row_id = await insert_fn(session, owner_tenant_id)
        await session.commit()

    async with session_factory() as session:
        await TenantContext(tenant_id=other_tenant_id).apply(session)
        result = await session.execute(text(select_sql), {id_param: row_id})
        assert result.first() is None


def skip_without_postgres() -> None:
    pytest.importorskip("testcontainers")
