"""Authenticated principal (doc 06)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

AuthMethod = Literal["bearer", "cookie"]


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: UUID
    session_id: UUID
    email: str
    token_version: int
    platform_roles: frozenset[str]
    tenant_id: UUID | None = None
    tenant_role: str | None = None
    permissions: frozenset[str] = frozenset()
    auth_method: AuthMethod = "bearer"

    def has_permission(self, permission: str) -> bool:
        if permission in self.permissions:
            return True
        module = permission.split(":", 1)[0]
        return f"{module}:*" in self.permissions

    def has_platform_role(self, role: str) -> bool:
        return role in self.platform_roles
