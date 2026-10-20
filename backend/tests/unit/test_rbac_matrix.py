"""Role permission matrix (doc 06 §4)."""

from __future__ import annotations

from app.modules.tenancy.permissions import (
    PERM_BILLING_MANAGE,
    PERM_CONVERSATIONS_REPLY,
    PERM_DATA_EXPORT,
    PERM_SETTINGS_BUSINESS_READ,
    PERM_SETTINGS_BUSINESS_WRITE,
    PERM_TEAM_INVITE_AGENT,
    PERM_TEAM_MANAGE,
)
from app.shared.rbac import permissions_for_tenant_role


def test_owner_has_billing_and_team_manage() -> None:
    perms = permissions_for_tenant_role("owner")
    assert PERM_BILLING_MANAGE in perms
    assert PERM_TEAM_MANAGE in perms
    assert PERM_DATA_EXPORT in perms


def test_manager_can_invite_agents_not_billing() -> None:
    perms = permissions_for_tenant_role("manager")
    assert PERM_TEAM_INVITE_AGENT in perms
    assert PERM_TEAM_MANAGE not in perms
    assert PERM_BILLING_MANAGE not in perms
    assert PERM_SETTINGS_BUSINESS_WRITE in perms


def test_agent_read_only_business_settings() -> None:
    perms = permissions_for_tenant_role("agent")
    assert PERM_SETTINGS_BUSINESS_READ in perms
    assert PERM_SETTINGS_BUSINESS_WRITE not in perms
    assert PERM_CONVERSATIONS_REPLY in perms
