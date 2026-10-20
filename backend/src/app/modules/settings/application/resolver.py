"""Layered settings resolver (R-CFG-03, R-CFG-04)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.errors.exceptions import PermissionDeniedError
from app.modules.settings.application.ports import EntitlementCheckerPort, SettingValueStorePort
from app.modules.settings.domain.definitions import ScopeLayer, SettingDefinition
from app.modules.settings.domain.registry import SettingsRegistry
from app.shared.context import SettingsResolveContext

TENANT_LAYERS: tuple[ScopeLayer, ...] = (
    "default",
    "platform",
    "plan",
    "tenant",
    "channel",
    "conversation",
)
USER_LAYERS: tuple[ScopeLayer, ...] = ("default", "platform", "user")


class SettingsResolver:
    def __init__(
        self,
        registry: SettingsRegistry,
        store: SettingValueStorePort,
        entitlements: EntitlementCheckerPort,
    ) -> None:
        self._registry = registry
        self._store = store
        self._entitlements = entitlements

    async def resolve(self, key: str, ctx: SettingsResolveContext) -> Any:
        definition = self._registry.get(key)
        if definition.entitlement:
            tenant = str(ctx.tenant_id) if ctx.tenant_id else None
            if not await self._entitlements.has_entitlement(definition.entitlement, tenant):
                raise PermissionDeniedError(
                    details={"entitlement": definition.entitlement},
                    code="settings.entitlement_required",
                )
        layers = TENANT_LAYERS if definition.chain == "tenant" else USER_LAYERS
        resolved: Any = definition.default

        for layer in layers:
            if layer != "default" and layer not in definition.overridable_at:
                continue
            scope_id = self._scope_id_for_layer(layer, ctx)
            value = await self._store.get_value(layer, scope_id, key, rls_tenant_id=ctx.tenant_id)
            if value is not None:
                resolved = definition.validate_value(value)

        if isinstance(resolved, int):
            resolved = await self._clamp_int(definition, ctx, resolved)
        return resolved

    async def _clamp_int(
        self,
        definition: SettingDefinition,
        ctx: SettingsResolveContext,
        value: int,
    ) -> int:
        min_bound = definition.schema.get("minimum")
        max_bound = definition.schema.get("maximum")
        for layer in definition.bounded_by:
            scope_id = self._scope_id_for_layer(layer, ctx)
            bound = await self._store.get_value(
                layer,
                scope_id,
                definition.key,
                rls_tenant_id=ctx.tenant_id,
            )
            if isinstance(bound, int):
                max_bound = bound if max_bound is None else min(max_bound, bound)
        if min_bound is not None:
            value = max(value, min_bound)
        if max_bound is not None:
            value = min(value, max_bound)
        return value

    def _scope_id_for_layer(self, layer: ScopeLayer, ctx: SettingsResolveContext) -> str | None:
        mapping: dict[ScopeLayer, UUID | None] = {
            "default": None,
            "platform": None,
            "plan": ctx.plan_id,
            "tenant": ctx.tenant_id,
            "channel": ctx.channel_id,
            "conversation": ctx.conversation_id,
            "user": ctx.user_id,
        }
        value = mapping.get(layer)
        return str(value) if value else None
