"""In-memory error_events adapter for unit tests."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from app.modules.audit.application.ports import ErrorEventsPort


class InMemoryErrorEventsPort(ErrorEventsPort):
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def record(
        self,
        *,
        tenant_id: UUID | None,
        module: str,
        code: str,
        message: str,
        trace_id: str,
        severity: str = "error",
        source_type: str | None = None,
        source_id: str | None = None,
        context: dict[str, Any] | None = None,
        session: Any | None = None,
    ) -> UUID:
        _ = session
        event_id = uuid4()
        self.events.append(
            {
                "id": event_id,
                "tenant_id": tenant_id,
                "module": module,
                "code": code,
                "message": message,
                "trace_id": trace_id,
                "severity": severity,
                "source_type": source_type,
                "source_id": source_id,
                "context": context or {},
            },
        )
        return event_id
