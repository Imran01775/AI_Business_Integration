"""In-memory realtime bus for tests."""

from __future__ import annotations

from typing import Any

from app.core.realtime.ports import RealtimePublisherPort


class InMemoryRealtimePublisher(RealtimePublisherPort):
    def __init__(self) -> None:
        self.messages: list[tuple[str, dict[str, Any]]] = []

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        self.messages.append((channel, payload))
