"""Setting definition model (R-CFG-02)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

SettingChain = Literal["tenant", "user"]
ScopeLayer = Literal[
    "default",
    "platform",
    "plan",
    "tenant",
    "channel",
    "conversation",
    "user",
]


@dataclass(frozen=True, slots=True)
class SettingDefinition:
    key: str
    chain: SettingChain
    value_type: type
    default: Any
    schema: dict[str, Any] = field(default_factory=dict)
    overridable_at: tuple[ScopeLayer, ...] = ("platform", "tenant")
    bounded_by: tuple[ScopeLayer, ...] = ("platform", "plan")
    edit_permission: str = "settings.business:write"
    entitlement: str | None = None
    is_secret: bool = False

    def validate_value(self, value: Any) -> Any:
        if self.value_type is bool and not isinstance(value, bool):
            raise TypeError(f"{self.key} expects bool")
        if self.value_type is int and not isinstance(value, int):
            raise TypeError(f"{self.key} expects int")
        if self.value_type is str and not isinstance(value, str):
            raise TypeError(f"{self.key} expects str")
        minimum = self.schema.get("minimum")
        maximum = self.schema.get("maximum")
        if isinstance(value, int):
            if minimum is not None and value < minimum:
                raise ValueError(f"{self.key} below minimum")
            if maximum is not None and value > maximum:
                raise ValueError(f"{self.key} above maximum")
        return value
