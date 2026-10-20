"""Sync code registry to setting_definitions table."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.session import session_scope
from app.core.ids import IdGenerator
from app.modules.settings.domain.registry import SettingsRegistry
from app.modules.settings.infrastructure.models import SettingDefinitionRow


def _serialize_default(value: object) -> dict[str, object]:
    return {"v": value}


class SettingDefinitionSync:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def sync_registry(self, registry: SettingsRegistry) -> int:
        updated = 0
        async with session_scope(self._session_factory) as session:
            for definition in registry.all_definitions():
                stmt = select(SettingDefinitionRow).where(
                    SettingDefinitionRow.key == definition.key
                )
                row = (await session.execute(stmt)).scalar_one_or_none()
                payload = {
                    "chain": definition.chain,
                    "value_type": definition.value_type.__name__,
                    "default_value": _serialize_default(definition.default),
                    "schema": definition.schema,
                    "overridable_at": list(definition.overridable_at),
                    "bounded_by": list(definition.bounded_by),
                    "edit_permission": definition.edit_permission,
                    "entitlement": definition.entitlement,
                    "is_secret": definition.is_secret,
                }
                if row is None:
                    session.add(
                        SettingDefinitionRow(
                            id=self._ids.uuid7(),
                            key=definition.key,
                            **payload,
                        ),
                    )
                    updated += 1
                else:
                    for field, value in payload.items():
                        setattr(row, field, value)
                    updated += 1
        return updated
