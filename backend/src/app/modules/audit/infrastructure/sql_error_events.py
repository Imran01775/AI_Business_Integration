"""PostgreSQL error_events adapter."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ids import IdGenerator
from app.modules.audit.application.ports import ErrorEventsPort
from app.modules.audit.infrastructure.models import ErrorEventRow


class SqlErrorEventsPort(ErrorEventsPort):
    def __init__(self, ids: IdGenerator) -> None:
        self._ids = ids

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
        if session is None or not isinstance(session, AsyncSession):
            raise RuntimeError("SqlErrorEventsPort requires an active AsyncSession")
        event_id = self._ids.uuid7()
        session.add(
            ErrorEventRow(
                id=event_id,
                tenant_id=tenant_id,
                module=module,
                code=code,
                severity=severity,
                source_type=source_type,
                source_id=source_id,
                message=message,
                context=context or {},
                trace_id=trace_id,
            ),
        )
        return event_id
