"""Shared domain event envelope."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ActorRef(BaseModel):
    type: Literal["user", "system", "customer"]
    id: str


class DomainEvent(BaseModel):
    event_id: UUID
    type: str
    version: int = 1
    occurred_at: datetime
    tenant_id: UUID | None = None
    trace_id: str
    actor: ActorRef
    payload: dict[str, Any] = Field(default_factory=dict)
