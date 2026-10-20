"""Processed event deduplication store."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.models.platform import ProcessedEvent
from app.core.db.session import session_scope
from app.core.events.consumer import ProcessedEventStore
from app.core.ids import IdGenerator


class PostgresProcessedEventStore(ProcessedEventStore):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._ids = ids

    async def was_processed(self, consumer: str, event_id: str) -> bool:
        async with session_scope(self._session_factory) as session:
            stmt = select(ProcessedEvent.id).where(
                ProcessedEvent.consumer_name == consumer,
                ProcessedEvent.event_id == UUID(event_id),
            )
            return (await session.execute(stmt)).scalar_one_or_none() is not None

    async def mark_processed(self, consumer: str, event_id: str) -> None:
        async with session_scope(self._session_factory) as session:
            session.add(
                ProcessedEvent(
                    id=self._ids.uuid7(),
                    consumer_name=consumer,
                    event_id=UUID(event_id),
                ),
            )
