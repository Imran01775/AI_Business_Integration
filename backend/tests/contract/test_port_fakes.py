from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.core.cache.memory import InMemoryCache
from app.core.email.memory import InMemoryEmailSender
from app.core.email.ports import EmailMessage
from app.core.events.in_memory import InMemoryEventBus
from app.core.jobs.memory import InMemoryJobQueue
from app.core.storage.local import LocalObjectStorage
from app.shared.events import ActorRef, DomainEvent


@pytest.mark.asyncio
async def test_cache_get_or_set_single_flight() -> None:
    cache = InMemoryCache()
    calls = 0

    async def factory() -> bytes:
        nonlocal calls
        calls += 1
        return b"value"

    first = await cache.get_or_set("k", 60, factory)
    second = await cache.get_or_set("k", 60, factory)
    assert first == second == b"value"
    assert calls == 1


@pytest.mark.asyncio
async def test_job_queue_enqueue() -> None:
    queue = InMemoryJobQueue()
    job_id = await queue.enqueue("demo", 1, foo="bar")
    assert job_id
    assert queue.jobs[0][0] == "demo"


@pytest.mark.asyncio
async def test_object_storage_roundtrip(tmp_path: Path) -> None:
    storage = LocalObjectStorage(tmp_path)
    await storage.put_bytes("a/b.txt", b"hello", "text/plain")
    assert await storage.get_bytes("a/b.txt") == b"hello"


@pytest.mark.asyncio
async def test_event_bus_publish() -> None:
    bus = InMemoryEventBus()
    event = DomainEvent(
        event_id=uuid4(),
        type="demo.event",
        occurred_at=datetime.now(UTC),
        trace_id="trace",
        actor=ActorRef(type="system", id="x"),
    )
    message_id = await bus.publish("events:demo", event)
    assert message_id


@pytest.mark.asyncio
async def test_email_sender_memory() -> None:
    sender = InMemoryEmailSender()
    await sender.send(EmailMessage(to="a@b.com", subject="s", body_text="hi"))
    assert len(sender.sent) == 1
