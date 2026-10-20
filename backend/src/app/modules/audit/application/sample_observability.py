"""Sample use case writing audit + error_events in one transaction."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.db.tenant import TenantContext
from app.core.db.uow import UnitOfWork
from app.modules.audit.application.ports import AuditPort, ErrorEventsPort


async def record_sample_business_failure(
    uow: UnitOfWork,
    audit: AuditPort,
    error_events: ErrorEventsPort,
    *,
    tenant_id: UUID,
    trace_id: str,
    actor_id: str | None,
    error_code: str,
    message: str,
    entity_type: str,
    entity_id: str,
    context: dict[str, Any] | None = None,
) -> UUID:
    async with uow:
        await uow.set_tenant(TenantContext(tenant_id=tenant_id))
        event_id = await error_events.record(
            tenant_id=tenant_id,
            module="audit",
            code=error_code,
            message=message,
            trace_id=trace_id,
            context=context,
            session=uow.session,
        )
        await audit.record(
            action="error_events.record",
            entity_type=entity_type,
            entity_id=entity_id,
            tenant_id=str(tenant_id),
            actor_id=actor_id,
            before=None,
            after={"error_event_id": str(event_id), "code": error_code},
            trace_id=trace_id,
            session=uow.session,
        )
        return event_id
