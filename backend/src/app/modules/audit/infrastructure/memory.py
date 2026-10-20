"""In-memory audit adapter until Phase 02."""

from __future__ import annotations

from typing import Any

from app.modules.audit.application.ports import AuditPort


class InMemoryAuditPort(AuditPort):
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

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
        session: object | None = None,
    ) -> None:
        _ = session
        self.entries.append(
            {
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "tenant_id": tenant_id,
                "actor_id": actor_id,
                "before": before,
                "after": after,
                "trace_id": trace_id,
            },
        )
