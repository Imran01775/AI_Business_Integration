"""Tenancy permission constants and role matrix (doc 06 §4)."""

from __future__ import annotations

from typing import Final

PERM_BILLING_MANAGE: Final = "billing:manage"
PERM_TEAM_MANAGE: Final = "team:manage"
PERM_TEAM_INVITE_AGENT: Final = "team:invite_agent"
PERM_CHANNELS_MANAGE: Final = "channels:manage"
PERM_SETTINGS_BUSINESS_WRITE: Final = "settings.business:write"
PERM_SETTINGS_BUSINESS_READ: Final = "settings.business:read"
PERM_CONVERSATIONS_REPLY: Final = "conversations:reply"
PERM_LEARNING_APPROVE: Final = "learning:approve"
PERM_DATA_EXPORT: Final = "data:export"
PERM_USER_SETTINGS: Final = "settings.user:write"

TENANT_ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "owner": (
        PERM_BILLING_MANAGE,
        PERM_TEAM_MANAGE,
        PERM_CHANNELS_MANAGE,
        PERM_SETTINGS_BUSINESS_WRITE,
        PERM_SETTINGS_BUSINESS_READ,
        PERM_CONVERSATIONS_REPLY,
        PERM_LEARNING_APPROVE,
        PERM_DATA_EXPORT,
        PERM_USER_SETTINGS,
    ),
    "manager": (
        PERM_TEAM_INVITE_AGENT,
        PERM_SETTINGS_BUSINESS_WRITE,
        PERM_SETTINGS_BUSINESS_READ,
        PERM_CONVERSATIONS_REPLY,
        PERM_LEARNING_APPROVE,
        PERM_USER_SETTINGS,
    ),
    "agent": (
        PERM_SETTINGS_BUSINESS_READ,
        PERM_CONVERSATIONS_REPLY,
        PERM_USER_SETTINGS,
    ),
}
