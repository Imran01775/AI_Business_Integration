"""Cron registration with Redis leader lock."""

from __future__ import annotations

import structlog
from redis.asyncio import Redis

logger = structlog.get_logger(__name__)


class CronLeaderLock:
    def __init__(self, redis: Redis, lock_key: str = "cron:leader", ttl_seconds: int = 55) -> None:
        self._redis = redis
        self._lock_key = lock_key
        self._ttl = ttl_seconds

    async def acquire(self, holder_id: str) -> bool:
        acquired = await self._redis.set(self._lock_key, holder_id, nx=True, ex=self._ttl)
        return bool(acquired)

    async def release(self, holder_id: str) -> None:
        current = await self._redis.get(self._lock_key)
        if current and current.decode() == holder_id:
            await self._redis.delete(self._lock_key)
