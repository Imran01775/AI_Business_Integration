"""Role → permission mapping (doc 06 §4)."""

from __future__ import annotations

from typing import Final

from app.modules.identity.permissions import PLATFORM_ROLE_PERMISSIONS
from app.modules.tenancy.permissions import TENANT_ROLE_PERMISSIONS

ALL_TENANT_ROLES: Final = frozenset(TENANT_ROLE_PERMISSIONS)
ALL_PLATFORM_ROLES: Final = frozenset(PLATFORM_ROLE_PERMISSIONS)


def permissions_for_tenant_role(role: str) -> frozenset[str]:
    return frozenset(TENANT_ROLE_PERMISSIONS.get(role, ()))


def permissions_for_platform_roles(roles: frozenset[str]) -> frozenset[str]:
    perms: set[str] = set()
    for role in roles:
        perms.update(PLATFORM_ROLE_PERMISSIONS.get(role, ()))
    return frozenset(perms)
