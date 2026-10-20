"""In-memory outbox and event bus for unit tests."""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events.ports import EventBusPort, OutboxPort
from app.shared.events import DomainEvent


class InMemoryOutbox(OutboxPort):
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    async def enqueue(self, session: AsyncSession, event: DomainEvent) -> None:
        self.rows.append(
            {
                "id": str(uuid4()),
                "event": event.model_dump(mode="json"),
                "published": False,
            },
        )

    async def fetch_pending(self, limit: int = 100) -> list[dict[str, Any]]:
        pending = [r for r in self.rows if not r["published"]]
        return pending[:limit]

    async def mark_published(self, outbox_id: str) -> None:
        for row in self.rows:
            if row["id"] == outbox_id:
                row["published"] = True
                return


class InMemoryEventBus(EventBusPort):
    def __init__(self) -> None:
        self.streams: dict[str, list[tuple[str, DomainEvent]]] = {}
        self._groups: set[tuple[str, str]] = set()

    async def publish(self, stream: str, event: DomainEvent) -> str:
        message_id = str(uuid4())
        self.streams.setdefault(stream, []).append((message_id, event))
        return message_id

    async def ensure_consumer_group(self, stream: str, group: str) -> None:
        self._groups.add((stream, group))

    async def read_group(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 10,
        block_ms: int = 1000,
    ) -> list[tuple[str, DomainEvent]]:
        _ = (group, consumer, block_ms)
        messages = self.streams.get(stream, [])[:count]
        return messages

    async def ack(self, stream: str, group: str, message_id: str) -> None:
        _ = (stream, group)
        if stream in self.streams:
            self.streams[stream] = [
                (mid, ev) for mid, ev in self.streams[stream] if mid != message_id
            ]


def event_to_stream_fields(event: DomainEvent) -> dict[str, str]:
    return {"data": json.dumps(event.model_dump(mode="json"))}
