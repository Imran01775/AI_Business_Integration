"""User-scoped routes (/api/v1/me)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.auth.dependencies import require_principal
from app.modules.settings.application.resolver import SettingsResolver
from app.shared.context import SettingsResolveContext
from app.shared.principal import Principal

router = APIRouter(prefix="/api/v1/me", tags=["me"])


class UserSettingsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    values: dict[str, Any] = Field(default_factory=dict)


@router.get("/settings")
async def get_user_settings(
    principal: Annotated[Principal, Depends(require_principal)],
    request: Request,
) -> dict[str, Any]:
    container = request.app.state.container
    registry = container.settings_registry
    ctx = SettingsResolveContext(user_id=principal.user_id)
    schema: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for definition in registry.all_definitions():
        if definition.chain != "user":
            continue
        schema[definition.key] = {
            "type": definition.value_type.__name__,
            "default": definition.default,
        }
        values[definition.key] = await container.settings_resolver.resolve(definition.key, ctx)
    return {"schema": schema, "values": values}


@router.patch("/settings")
async def patch_user_settings(
    body: UserSettingsPatch,
    principal: Annotated[Principal, Depends(require_principal)],
    request: Request,
) -> dict[str, Any]:
    container = request.app.state.container
    registry = container.settings_registry
    resolver: SettingsResolver = container.settings_resolver
    ctx = SettingsResolveContext(user_id=principal.user_id)
    for key, value in body.values.items():
        definition = registry.get(key)
        if definition.chain != "user":
            continue
        validated = definition.validate_value(value)
        await container.setting_store.set_value(
            "user",
            str(principal.user_id),
            key,
            validated,
            changed_by=str(principal.user_id),
        )
    values = {
        d.key: await resolver.resolve(d.key, ctx)
        for d in registry.all_definitions()
        if d.chain == "user"
    }
    return {"values": values}
