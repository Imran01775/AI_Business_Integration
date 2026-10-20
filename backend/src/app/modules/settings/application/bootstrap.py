"""Build registry from module settings.py files."""

from __future__ import annotations

from app.modules.settings.domain.registry import SettingsRegistry
from app.modules.settings.settings import platform_settings
from app.modules.settings.user_settings import user_settings_definitions


def build_settings_registry() -> SettingsRegistry:
    registry = SettingsRegistry()
    registry.register_many(platform_settings())
    registry.register_many(user_settings_definitions())
    return registry
