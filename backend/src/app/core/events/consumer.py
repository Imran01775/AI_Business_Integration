"""Idempotent event consumer base."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.events.ports import EventBusPort
from app.shared.events import DomainEvent


class ProcessedEventStore(ABC):
    @abstractmethod
    async def was_processed(self, consumer: str, event_id: str) -> bool: ...

    @abstractmethod
    async def mark_processed(self, consumer: str, event_id: str) -> None: ...


class InMemoryProcessedEventStore(ProcessedEventStore):
    def __init__(self) -> None:
        self._seen: set[tuple[str, str]] = set()

    async def was_processed(self, consumer: str, event_id: str) -> bool:
        return (consumer, event_id) in self._seen

    async def mark_processed(self, consumer: str, event_id: str) -> None:
        self._seen.add((consumer, event_id))


class IdempotentConsumer(ABC):
    def __init__(
        self,
        bus: EventBusPort,
        store: ProcessedEventStore,
        stream: str,
        group: str,
        consumer_name: str,
    ) -> None:
        self._bus = bus
        self._store = store
        self._stream = stream
        self._group = group
        self._consumer_name = consumer_name

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None: ...

    async def poll_once(self) -> int:
        await self._bus.ensure_consumer_group(self._stream, self._group)
        messages = await self._bus.read_group(
            self._stream,
            self._group,
            self._consumer_name,
            count=10,
            block_ms=100,
        )
        handled = 0
        for message_id, event in messages:
            key = str(event.event_id)
            if await self._store.was_processed(self._consumer_name, key):
                await self._bus.ack(self._stream, self._group, message_id)
                continue
            await self.handle(event)
            await self._store.mark_processed(self._consumer_name, key)
            await self._bus.ack(self._stream, self._group, message_id)
            handled += 1
        return handled
