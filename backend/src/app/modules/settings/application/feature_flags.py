"""Feature flags via settings resolver (flags.*)."""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

from app.modules.settings.application.resolver import SettingsResolver
from app.shared.context import SettingsResolveContext


class FeatureFlagsPort(ABC):
    @abstractmethod
    async def is_enabled(
        self, flag_key: str, ctx: SettingsResolveContext, subject_id: str
    ) -> bool: ...


class SettingsFeatureFlags(FeatureFlagsPort):
    def __init__(self, resolver: SettingsResolver) -> None:
        self._resolver = resolver

    async def is_enabled(self, flag_key: str, ctx: SettingsResolveContext, subject_id: str) -> bool:
        key = f"flags.{flag_key}"
        value = await self._resolver.resolve(key, ctx)
        if isinstance(value, bool):
            enabled = value
        elif isinstance(value, dict):
            enabled = bool(value.get("enabled", False))
            rollout = int(value.get("rollout_percent", 100))
            if enabled and rollout < 100:
                bucket = (
                    int(hashlib.sha256(f"{flag_key}:{subject_id}".encode()).hexdigest(), 16) % 100
                )
                enabled = bucket < rollout
        else:
            enabled = bool(value)
        return enabled
