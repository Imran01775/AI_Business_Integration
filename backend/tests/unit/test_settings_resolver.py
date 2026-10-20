from __future__ import annotations

from uuid import uuid4

import pytest

from app.modules.settings.application.bootstrap import build_settings_registry
from app.modules.settings.application.resolver import SettingsResolver
from app.modules.settings.domain.definitions import SettingDefinition
from app.modules.settings.infrastructure.entitlements import AllowAllEntitlements
from app.modules.settings.infrastructure.memory_store import InMemorySettingValueStore
from app.shared.context import SettingsResolveContext


@pytest.fixture
def resolver() -> SettingsResolver:
    registry = build_settings_registry()
    registry.register(
        SettingDefinition(
            key="voice.max_duration_seconds",
            chain="tenant",
            value_type=int,
            default=60,
            schema={"minimum": 5, "maximum": 300},
            overridable_at=("platform", "plan", "tenant"),
            bounded_by=("platform", "plan"),
        ),
    )
    return SettingsResolver(registry, InMemorySettingValueStore(), AllowAllEntitlements())


@pytest.mark.asyncio
async def test_tenant_chain_wins_over_default(resolver: SettingsResolver) -> None:
    tenant = uuid4()
    await resolver._store.set_value("tenant", str(tenant), "voice.max_duration_seconds", 90)
    value = await resolver.resolve(
        "voice.max_duration_seconds",
        SettingsResolveContext(tenant_id=tenant),
    )
    assert value == 90


@pytest.mark.asyncio
async def test_user_chain_separate_from_tenant(resolver: SettingsResolver) -> None:
    user = uuid4()
    await resolver._store.set_value("user", str(user), "user.theme", "dark")
    assert await resolver.resolve("user.theme", SettingsResolveContext(user_id=user)) == "dark"
    assert await resolver.resolve("user.theme", SettingsResolveContext()) == "system"


@pytest.mark.asyncio
async def test_clamping_to_plan_cap(resolver: SettingsResolver) -> None:
    plan = uuid4()
    tenant = uuid4()
    await resolver._store.set_value("plan", str(plan), "voice.max_duration_seconds", 80)
    await resolver._store.set_value("tenant", str(tenant), "voice.max_duration_seconds", 120)
    value = await resolver.resolve(
        "voice.max_duration_seconds",
        SettingsResolveContext(tenant_id=tenant, plan_id=plan),
    )
    assert value == 80
