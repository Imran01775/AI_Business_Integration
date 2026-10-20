"""PostgreSQL message template store."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.session import session_scope
from app.core.db.tenant import TenantContext
from app.core.ids import IdGenerator
from app.modules.settings.application.ports import TemplateDetail, TemplateStorePort
from app.modules.settings.infrastructure.models import MessageTemplateHistoryRow, MessageTemplateRow


class SqlTemplateStore(TemplateStorePort):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def _prepare(self, session: AsyncSession, tenant_id: UUID | None) -> None:
        if tenant_id is not None:
            await TenantContext(tenant_id=tenant_id).apply(session)

    async def upsert(
        self,
        key: str,
        locale: str,
        body: str,
        variables: list[str],
        *,
        tenant_id: UUID | None = None,
    ) -> int:
        async with session_scope(self._session_factory) as session:
            await self._prepare(session, tenant_id)
            stmt = select(MessageTemplateRow).where(
                MessageTemplateRow.key == key,
                MessageTemplateRow.locale == locale,
                MessageTemplateRow.tenant_id == tenant_id
                if tenant_id is not None
                else MessageTemplateRow.tenant_id.is_(None),
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                row = MessageTemplateRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    key=key,
                    locale=locale,
                    body=body,
                    variables=variables,
                    version=1,
                )
                session.add(row)
                version = 1
            else:
                row.version += 1
                row.body = body
                row.variables = variables
                version = row.version
            session.add(
                MessageTemplateHistoryRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    key=key,
                    locale=locale,
                    body=body,
                    variables=variables,
                    version=version,
                ),
            )
            return version

    async def get_template(
        self,
        key: str,
        locale: str,
        *,
        tenant_id: UUID | None = None,
    ) -> tuple[str, list[str]] | None:
        async with session_scope(self._session_factory) as session:
            await self._prepare(session, tenant_id)
            stmt = select(MessageTemplateRow).where(
                MessageTemplateRow.key == key,
                MessageTemplateRow.locale == locale,
                MessageTemplateRow.is_active.is_(True),
                MessageTemplateRow.tenant_id == tenant_id
                if tenant_id is not None
                else MessageTemplateRow.tenant_id.is_(None),
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                return None
            return row.body, list(row.variables)

    async def get_template_detail(
        self,
        key: str,
        locale: str,
        *,
        tenant_id: UUID | None = None,
    ) -> TemplateDetail | None:
        async with session_scope(self._session_factory) as session:
            await self._prepare(session, tenant_id)
            stmt = select(MessageTemplateRow).where(
                MessageTemplateRow.key == key,
                MessageTemplateRow.locale == locale,
                MessageTemplateRow.is_active.is_(True),
                MessageTemplateRow.tenant_id == tenant_id
                if tenant_id is not None
                else MessageTemplateRow.tenant_id.is_(None),
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                return None
            return TemplateDetail(
                body=row.body,
                variables=list(row.variables),
                version=row.version,
                locale=row.locale,
                updated_at=row.updated_at,
            )

    async def rollback(
        self,
        key: str,
        locale: str,
        to_version: int,
        *,
        tenant_id: UUID | None = None,
    ) -> None:
        async with session_scope(self._session_factory) as session:
            await self._prepare(session, tenant_id)
            hist_stmt = select(MessageTemplateHistoryRow).where(
                MessageTemplateHistoryRow.key == key,
                MessageTemplateHistoryRow.locale == locale,
                MessageTemplateHistoryRow.version == to_version,
                MessageTemplateHistoryRow.tenant_id == tenant_id
                if tenant_id is not None
                else MessageTemplateHistoryRow.tenant_id.is_(None),
            )
            hist = (await session.execute(hist_stmt)).scalar_one_or_none()
            if hist is None:
                raise LookupError(f"template history version {to_version} not found")
            stmt = select(MessageTemplateRow).where(
                MessageTemplateRow.key == key,
                MessageTemplateRow.locale == locale,
                MessageTemplateRow.tenant_id == tenant_id
                if tenant_id is not None
                else MessageTemplateRow.tenant_id.is_(None),
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                row = MessageTemplateRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    key=key,
                    locale=locale,
                    body=hist.body,
                    variables=list(hist.variables),
                    version=to_version,
                )
                session.add(row)
            else:
                row.version = to_version
                row.body = hist.body
                row.variables = list(hist.variables)
            session.add(
                MessageTemplateHistoryRow(
                    id=self._ids.uuid7(),
                    tenant_id=tenant_id,
                    key=key,
                    locale=locale,
                    body=hist.body,
                    variables=list(hist.variables),
                    version=row.version,
                ),
            )
