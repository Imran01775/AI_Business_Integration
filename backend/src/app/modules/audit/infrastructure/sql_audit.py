"""PostgreSQL audit log adapter."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ids import IdGenerator
from app.modules.audit.application.ports import AuditPort
from app.modules.audit.infrastructure.models import AuditLogRow


class SqlAuditPort(AuditPort):
    def __init__(self, ids: IdGenerator) -> None:
        self._ids = ids

    async def record(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        tenant_id: str | None,
        actor_id: str | None,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
        trace_id: str,
        session: Any | None = None,
    ) -> None:
        if session is None or not isinstance(session, AsyncSession):
            raise RuntimeError("SqlAuditPort requires an active AsyncSession")
        parsed_tenant: UUID | None = UUID(tenant_id) if tenant_id else None
        session.add(
            AuditLogRow(
                id=self._ids.uuid7(),
                tenant_id=parsed_tenant,
                actor_type="user" if actor_id else "system",
                actor_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                before=before,
                after=after,
                trace_id=trace_id,
            ),
        )
