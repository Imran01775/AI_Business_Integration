"""Platform settings declarations for the settings module."""

from __future__ import annotations

from app.modules.settings.domain.definitions import SettingDefinition


def platform_settings() -> list[SettingDefinition]:
    return [
        SettingDefinition(
            key="platform.maintenance_mode",
            chain="tenant",
            value_type=bool,
            default=False,
            overridable_at=("platform", "tenant"),
            bounded_by=("platform",),
            edit_permission="platform.admin:write",
        ),
        SettingDefinition(
            key="auth.access_token_minutes",
            chain="tenant",
            value_type=int,
            default=15,
            schema={"minimum": 5, "maximum": 60},
            overridable_at=("platform",),
            bounded_by=("platform",),
            edit_permission="platform.admin:write",
        ),
        SettingDefinition(
            key="auth.refresh_token_days",
            chain="tenant",
            value_type=int,
            default=30,
            schema={"minimum": 1, "maximum": 90},
            overridable_at=("platform",),
            bounded_by=("platform",),
            edit_permission="platform.admin:write",
        ),
        SettingDefinition(
            key="auth.max_sessions",
            chain="tenant",
            value_type=int,
            default=10,
            schema={"minimum": 1, "maximum": 50},
            overridable_at=("platform",),
            bounded_by=("platform",),
            edit_permission="platform.admin:write",
        ),
        SettingDefinition(
            key="flags.example_feature",
            chain="tenant",
            value_type=dict,
            default={"enabled": False, "rollout_percent": 0},
            schema={"type": "object"},
            overridable_at=("platform", "plan", "tenant"),
            bounded_by=("platform", "plan"),
            edit_permission="platform.admin:write",
        ),
    ]
