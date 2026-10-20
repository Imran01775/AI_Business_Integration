"""Request and resolution context shared across modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestContext:
    trace_id: str
    request_id: str
    tenant_id: UUID | None = None
    user_id: UUID | None = None
    locale: str = "en"
    client_type: Literal["web", "mobile", "system"] = "web"


@dataclass(frozen=True, slots=True)
class SettingsResolveContext:
    """Scope for layered settings resolution (R-CFG-03)."""

    tenant_id: UUID | None = None
    plan_id: UUID | None = None
    channel_id: UUID | None = None
    conversation_id: UUID | None = None
    user_id: UUID | None = None
