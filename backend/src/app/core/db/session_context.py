"""Apply tenant / user RLS context on a SQLAlchemy session."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.tenant import TenantContext


async def apply_user_context(session: AsyncSession, user_id: UUID | None) -> None:
    value = str(user_id) if user_id else ""
    await session.execute(
        text("SELECT set_config('app.user_id', :user_id, true)"),
        {"user_id": value},
    )


async def with_tenant_session(
    factory: async_sessionmaker[AsyncSession],
    tenant_id: UUID | None,
    *,
    user_id: UUID | None = None,
) -> AsyncSession:
    """Return a session with optional tenant/user context (caller must close/commit)."""
    session = factory()
    if tenant_id is not None:
        await TenantContext(tenant_id=tenant_id).apply(session)
    if user_id is not None:
        await apply_user_context(session, user_id)
    return session
