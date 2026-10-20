"""Outbox relay: pending rows → event bus."""

from __future__ import annotations

import structlog

from app.core.events.ports import EventBusPort, OutboxPort
from app.shared.events import DomainEvent

logger = structlog.get_logger(__name__)


class OutboxRelay:
    def __init__(
        self, outbox: OutboxPort, bus: EventBusPort, stream_prefix: str = "events"
    ) -> None:
        self._outbox = outbox
        self._bus = bus
        self._stream_prefix = stream_prefix

    def _stream_for(self, event: DomainEvent) -> str:
        topic = event.type.split(".")[0] if "." in event.type else "default"
        return f"{self._stream_prefix}:{topic}"

    async def run_once(self, batch_size: int = 50) -> int:
        pending = await self._outbox.fetch_pending(limit=batch_size)
        published = 0
        for row in pending:
            event = DomainEvent.model_validate(row["event"])
            stream = self._stream_for(event)
            await self._bus.publish(stream, event)
            await self._outbox.mark_published(row["id"])
            published += 1
            logger.info("outbox_published", event_type=event.type, stream=stream)
        return published
