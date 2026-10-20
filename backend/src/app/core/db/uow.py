"""Unit of Work with outbox collection (R-DB-08)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.tenant import TenantContext
from app.core.events.ports import OutboxPort
from app.shared.events import DomainEvent


class UnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        outbox: OutboxPort,
    ) -> None:
        self._session_factory = session_factory
        self._outbox = outbox
        self._session: AsyncSession | None = None
        self._pending_events: list[DomainEvent] = []

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork not started")
        return self._session

    async def __aenter__(self) -> UnitOfWork:
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._session is None:
            return
        try:
            if exc_type is None:
                for event in self._pending_events:
                    await self._outbox.enqueue(self._session, event)
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
            self._pending_events.clear()

    def collect_event(self, event: DomainEvent) -> None:
        self._pending_events.append(event)

    async def set_tenant(self, ctx: TenantContext) -> None:
        await ctx.apply(self.session)
