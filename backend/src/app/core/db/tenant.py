"""PostgreSQL tenant context for RLS (R-TEN-02)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: UUID

    async def apply(self, session: AsyncSession) -> None:
        await session.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": str(self.tenant_id)},
        )
