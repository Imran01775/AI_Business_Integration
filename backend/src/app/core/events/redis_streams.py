"""Redis Streams event bus adapter."""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis

from app.core.events.ports import EventBusPort
from app.shared.events import DomainEvent


class RedisStreamsEventBus(EventBusPort):
    def __init__(self, client: redis.Redis) -> None:
        self._redis = client

    async def publish(self, stream: str, event: DomainEvent) -> str:
        payload: dict[str, str] = {"data": json.dumps(event.model_dump(mode="json"))}
        message_id = await self._redis.xadd(stream, payload)  # type: ignore[arg-type]
        if isinstance(message_id, bytes):
            return message_id.decode()
        return str(message_id)

    async def ensure_consumer_group(self, stream: str, group: str) -> None:
        try:
            await self._redis.xgroup_create(stream, group, id="0-0", mkstream=True)
        except redis.ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    async def read_group(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 10,
        block_ms: int = 1000,
    ) -> list[tuple[str, DomainEvent]]:
        raw: list[Any] = await self._redis.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams={stream: ">"},
            count=count,
            block=block_ms,
        )
        results: list[tuple[str, DomainEvent]] = []
        if not raw:
            return results
        for _stream_name, messages in raw:
            for message_id, fields in messages:
                data = fields.get(b"data") or fields.get("data")
                if isinstance(data, bytes):
                    data = data.decode()
                event = DomainEvent.model_validate_json(data)
                mid = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
                results.append((mid, event))
        return results

    async def ack(self, stream: str, group: str, message_id: str) -> None:
        await self._redis.xack(stream, group, message_id)
