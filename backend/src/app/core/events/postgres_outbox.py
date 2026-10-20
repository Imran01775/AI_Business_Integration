"""Transactional outbox backed by PostgreSQL."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.models.platform import OutboxEvent
from app.core.db.session import session_scope
from app.core.events.ports import OutboxPort
from app.core.ids import IdGenerator
from app.shared.events import DomainEvent


class PostgresOutbox(OutboxPort):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def enqueue(self, session: AsyncSession, event: DomainEvent) -> None:
        session.add(
            OutboxEvent(
                id=self._ids.uuid7(),
                tenant_id=event.tenant_id,
                topic=event.type,
                payload=event.model_dump(mode="json"),
                status="pending",
                attempts=0,
            ),
        )

    async def fetch_pending(self, limit: int = 100) -> list[dict[str, Any]]:
        async with session_scope(self._session_factory) as session:
            stmt = (
                select(OutboxEvent)
                .where(OutboxEvent.status == "pending")
                .order_by(OutboxEvent.created_at)
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [
                {
                    "id": str(row.id),
                    "event": row.payload,
                    "published": row.status == "published",
                }
                for row in rows
            ]

    async def mark_published(self, outbox_id: str) -> None:
        async with session_scope(self._session_factory) as session:
            stmt = (
                update(OutboxEvent)
                .where(OutboxEvent.id == UUID(outbox_id))
                .values(status="published", published_at=datetime.now(UTC))
            )
            await session.execute(stmt)
