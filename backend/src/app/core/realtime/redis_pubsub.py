"""Redis pub/sub realtime publisher."""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis

from app.core.realtime.ports import RealtimePublisherPort


class RedisRealtimePublisher(RealtimePublisherPort):
    def __init__(self, client: redis.Redis) -> None:
        self._redis = client

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        await self._redis.publish(channel, json.dumps(payload))
