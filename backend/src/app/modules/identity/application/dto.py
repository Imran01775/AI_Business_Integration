"""Identity DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthResult:
    access_token: str
    refresh_token: str
    csrf_token: str | None
    user_id: UUID
    session_id: UUID


@dataclass(frozen=True, slots=True)
class SessionView:
    id: UUID
    client_type: str
    device_name: str | None
    ip_address: str | None
    last_seen_at: datetime
    created_at: datetime
    is_current: bool
