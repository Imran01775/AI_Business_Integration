"""In-memory setting values for unit tests."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.modules.settings.application.ports import SettingValueStorePort
from app.modules.settings.domain.definitions import ScopeLayer


class InMemorySettingValueStore(SettingValueStorePort):
    def __init__(self) -> None:
        self._values: dict[tuple[ScopeLayer, str | None, str], Any] = {}
        self._versions: dict[tuple[ScopeLayer, str | None, str], int] = {}
        self._history: list[dict[str, Any]] = []

    async def get_value(
        self,
        layer: ScopeLayer,
        scope_id: str | None,
        key: str,
        *,
        rls_tenant_id: UUID | None = None,
    ) -> Any | None:
        _ = rls_tenant_id
        return self._values.get((layer, scope_id, key))

    async def set_value(
        self,
        layer: ScopeLayer,
        scope_id: str | None,
        key: str,
        value: Any,
        *,
        rls_tenant_id: UUID | None = None,
        changed_by: str | None = None,
    ) -> int:
        _ = (rls_tenant_id, changed_by)
        version = self._versions.get((layer, scope_id, key), 0) + 1
        self._versions[(layer, scope_id, key)] = version
        self._values[(layer, scope_id, key)] = value
        self._history.append(
            {"layer": layer, "scope_id": scope_id, "key": key, "value": value, "version": version},
        )
        return version

    async def rollback_value(
        self,
        layer: ScopeLayer,
        scope_id: str | None,
        key: str,
        to_version: int,
        *,
        rls_tenant_id: UUID | None = None,
        changed_by: str | None = None,
    ) -> None:
        _ = (rls_tenant_id, changed_by)
        for entry in reversed(self._history):
            if (
                entry["layer"] == layer
                and entry["scope_id"] == scope_id
                and entry["key"] == key
                and entry["version"] == to_version
            ):
                await self.set_value(layer, scope_id, key, entry["value"])
                return
        raise LookupError(f"version {to_version} not found")
