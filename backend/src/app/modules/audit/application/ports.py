"""Audit and error-event ports (R-OBS-04, R-OBS-05)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class AuditPort(ABC):
    @abstractmethod
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
    ) -> None: ...


class ErrorEventsPort(ABC):
    @abstractmethod
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
    ) -> UUID: ...
