from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.core.events.in_memory import InMemoryEventBus, InMemoryOutbox
from app.core.events.relay import OutboxRelay
from app.shared.events import ActorRef, DomainEvent


@pytest.mark.asyncio
async def test_outbox_relay_publishes_to_bus() -> None:
    outbox = InMemoryOutbox()
    bus = InMemoryEventBus()
    relay = OutboxRelay(outbox, bus)
    event = DomainEvent(
        event_id=uuid4(),
        type="settings.changed",
        occurred_at=datetime.now(UTC),
        trace_id="t1",
        actor=ActorRef(type="system", id="test"),
        payload={"key": "platform.maintenance_mode"},
    )
    outbox.rows.append({"id": "1", "event": event.model_dump(mode="json"), "published": False})
    count = await relay.run_once()
    assert count == 1
    assert bus.streams
