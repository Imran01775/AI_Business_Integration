"""Standard API error envelope (R-API-04)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    trace_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorBody
