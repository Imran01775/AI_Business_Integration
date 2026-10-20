"""User-chain setting declarations (Phase 03)."""

from __future__ import annotations

from app.modules.settings.domain.definitions import SettingDefinition


def user_settings_definitions() -> list[SettingDefinition]:
    return [
        SettingDefinition(
            key="user.locale",
            chain="user",
            value_type=str,
            default="en",
            overridable_at=("platform", "user"),
            bounded_by=("platform",),
            edit_permission="settings.user:write",
        ),
        SettingDefinition(
            key="user.theme",
            chain="user",
            value_type=str,
            default="system",
            overridable_at=("platform", "user"),
            bounded_by=("platform",),
            edit_permission="settings.user:write",
        ),
        SettingDefinition(
            key="user.timezone_display",
            chain="user",
            value_type=str,
            default="UTC",
            overridable_at=("platform", "user"),
            bounded_by=("platform",),
            edit_permission="settings.user:write",
        ),
        SettingDefinition(
            key="user.availability_status",
            chain="user",
            value_type=str,
            default="available",
            overridable_at=("platform", "user"),
            bounded_by=("platform",),
            edit_permission="settings.user:write",
        ),
        SettingDefinition(
            key="user.notifications.email",
            chain="user",
            value_type=bool,
            default=True,
            overridable_at=("platform", "user"),
            bounded_by=("platform",),
            edit_permission="settings.user:write",
        ),
        SettingDefinition(
            key="user.notifications.push",
            chain="user",
            value_type=bool,
            default=True,
            overridable_at=("platform", "user"),
            bounded_by=("platform",),
            edit_permission="settings.user:write",
        ),
        SettingDefinition(
            key="user.notifications.in_app",
            chain="user",
            value_type=bool,
            default=True,
            overridable_at=("platform", "user"),
            bounded_by=("platform",),
            edit_permission="settings.user:write",
        ),
    ]
