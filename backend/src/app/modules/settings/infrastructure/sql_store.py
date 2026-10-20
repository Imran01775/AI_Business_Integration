"""PostgreSQL setting value store with history."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.session import session_scope
from app.core.db.tenant import TenantContext
from app.core.ids import IdGenerator
from app.modules.settings.application.ports import SettingValueStorePort
from app.modules.settings.domain.definitions import ScopeLayer
from app.modules.settings.infrastructure.models import SettingValueHistoryRow, SettingValueRow


def _tenant_column_value(
    layer: ScopeLayer, scope_id: str | None, rls_tenant_id: UUID | None
) -> UUID | None:
    if layer in ("tenant", "channel", "conversation"):
        if rls_tenant_id is not None:
            return rls_tenant_id
        if scope_id is not None and layer == "tenant":
            return UUID(scope_id)
    return None


def _json_value(value: Any) -> dict[str, Any]:
    return {"v": value}


def _unwrap_value(row_value: dict[str, Any]) -> Any:
    return row_value.get("v")


class SqlSettingValueStore(SettingValueStorePort):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def _prepare(self, session: AsyncSession, rls_tenant_id: UUID | None) -> None:
        if rls_tenant_id is not None:
            await TenantContext(tenant_id=rls_tenant_id).apply(session)

    async def get_value(
        self,
        layer: ScopeLayer,
        scope_id: str | None,
        key: str,
        *,
        rls_tenant_id: UUID | None = None,
    ) -> Any | None:
        tenant_id = _tenant_column_value(layer, scope_id, rls_tenant_id)
        async with session_scope(self._session_factory) as session:
            await self._prepare(session, rls_tenant_id)
            stmt = select(SettingValueRow).where(
                SettingValueRow.scope_layer == layer,
                SettingValueRow.scope_id == scope_id,
                SettingValueRow.key == key,
                SettingValueRow.tenant_id == tenant_id
                if tenant_id is not None
                else SettingValueRow.tenant_id.is_(None),
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                return None
            return _unwrap_value(row.value)

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
        tenant_id = _tenant_column_value(layer, scope_id, rls_tenant_id)
        async with session_scope(self._session_factory) as session:
            await self._prepare(session, rls_tenant_id)
            stmt = select(SettingValueRow).where(
                SettingValueRow.scope_layer == layer,
                SettingValueRow.scope_id == scope_id,
                SettingValueRow.key == key,
                SettingValueRow.tenant_id == tenant_id
                if tenant_id is not None
                else SettingValueRow.tenant_id.is_(None),
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                row = SettingValueRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    scope_layer=layer,
                    scope_id=scope_id,
                    key=key,
                    value=_json_value(value),
                    version=1,
                )
                session.add(row)
                version = 1
            else:
                row.version += 1
                row.value = _json_value(value)
                version = row.version
            session.add(
                SettingValueHistoryRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    scope_layer=layer,
                    scope_id=scope_id,
                    key=key,
                    value=_json_value(value),
                    version=version,
                    changed_by=changed_by,
                ),
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
        tenant_id = _tenant_column_value(layer, scope_id, rls_tenant_id)
        async with session_scope(self._session_factory) as session:
            await self._prepare(session, rls_tenant_id)
            hist_stmt = select(SettingValueHistoryRow).where(
                SettingValueHistoryRow.scope_layer == layer,
                SettingValueHistoryRow.scope_id == scope_id,
                SettingValueHistoryRow.key == key,
                SettingValueHistoryRow.version == to_version,
                SettingValueHistoryRow.tenant_id == tenant_id
                if tenant_id is not None
                else SettingValueHistoryRow.tenant_id.is_(None),
            )
            hist = (await session.execute(hist_stmt)).scalar_one_or_none()
            if hist is None:
                raise LookupError(f"history version {to_version} not found for {key}")
            value = _unwrap_value(hist.value)
            stmt = select(SettingValueRow).where(
                SettingValueRow.scope_layer == layer,
                SettingValueRow.scope_id == scope_id,
                SettingValueRow.key == key,
                SettingValueRow.tenant_id == tenant_id
                if tenant_id is not None
                else SettingValueRow.tenant_id.is_(None),
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                row = SettingValueRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    scope_layer=layer,
                    scope_id=scope_id,
                    key=key,
                    value=_json_value(value),
                    version=to_version,
                )
                session.add(row)
            else:
                row.version = to_version
                row.value = _json_value(value)
            session.add(
                SettingValueHistoryRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    scope_layer=layer,
                    scope_id=scope_id,
                    key=key,
                    value=_json_value(value),
                    version=row.version,
                    changed_by=changed_by,
                ),
            )
