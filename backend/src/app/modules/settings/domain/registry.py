"""Settings registry — collects definitions from modules."""

from __future__ import annotations

from app.modules.settings.domain.definitions import SettingDefinition


class SettingsRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, SettingDefinition] = {}

    def register(self, definition: SettingDefinition) -> None:
        if definition.key in self._definitions:
            raise ValueError(f"duplicate setting key: {definition.key}")
        self._definitions[definition.key] = definition

    def register_many(self, definitions: list[SettingDefinition]) -> None:
        for item in definitions:
            self.register(item)

    def get(self, key: str) -> SettingDefinition:
        if key not in self._definitions:
            raise KeyError(key)
        return self._definitions[key]

    def all_definitions(self) -> list[SettingDefinition]:
        return list(self._definitions.values())
