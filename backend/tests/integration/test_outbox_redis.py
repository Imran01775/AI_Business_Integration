from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
import redis.asyncio as redis

from app.core.events.consumer import IdempotentConsumer, InMemoryProcessedEventStore
from app.core.events.in_memory import InMemoryOutbox
from app.core.events.redis_streams import RedisStreamsEventBus
from app.core.events.relay import OutboxRelay
from app.shared.events import ActorRef, DomainEvent

pytestmark = pytest.mark.integration


class _DemoConsumer(IdempotentConsumer):
    def __init__(self, bus, store, handled: list[str]) -> None:
        super().__init__(bus, store, "events:settings", "demo", "c1")
        self._handled = handled

    async def handle(self, event: DomainEvent) -> None:
        self._handled.append(event.type)


@pytest.mark.asyncio
async def test_outbox_to_redis_idempotent_consumer() -> None:
    try:
        client = redis.from_url("redis://localhost:6379/15", decode_responses=False)
        await client.ping()
    except Exception:
        pytest.skip("Redis not available on localhost:6379")

    await client.flushdb()
    outbox = InMemoryOutbox()
    bus = RedisStreamsEventBus(client)
    relay = OutboxRelay(outbox, bus, stream_prefix="events")
    event = DomainEvent(
        event_id=uuid4(),
        type="settings.changed",
        occurred_at=datetime.now(UTC),
        trace_id="trace-redis",
        actor=ActorRef(type="system", id="it"),
        payload={"key": "flags.example_feature"},
    )
    handled: list[str] = []
    consumer = _DemoConsumer(bus, InMemoryProcessedEventStore(), handled)
    await bus.ensure_consumer_group("events:settings", "demo")

    outbox.rows.append({"id": "1", "event": event.model_dump(mode="json"), "published": False})
    assert await relay.run_once() == 1
    assert await consumer.poll_once() == 1
    assert handled == ["settings.changed"]
    assert await consumer.poll_once() == 0

    await client.aclose()
