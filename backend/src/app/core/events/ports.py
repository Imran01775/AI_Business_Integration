"""Event bus and outbox ports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.events import DomainEvent


class OutboxPort(ABC):
    @abstractmethod
    async def enqueue(self, session: AsyncSession, event: DomainEvent) -> None: ...

    @abstractmethod
    async def fetch_pending(self, limit: int = 100) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def mark_published(self, outbox_id: str) -> None: ...


class EventBusPort(ABC):
    @abstractmethod
    async def publish(self, stream: str, event: DomainEvent) -> str: ...

    @abstractmethod
    async def ensure_consumer_group(self, stream: str, group: str) -> None: ...

    @abstractmethod
    async def read_group(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 10,
        block_ms: int = 1000,
    ) -> list[tuple[str, DomainEvent]]: ...

    @abstractmethod
    async def ack(self, stream: str, group: str, message_id: str) -> None: ...
