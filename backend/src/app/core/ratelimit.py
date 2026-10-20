"""Simple Redis-backed rate limiter."""

from __future__ import annotations

import time

import redis.asyncio as redis


class RateLimiter:
    def __init__(self, client: redis.Redis, limit: int, window_seconds: int) -> None:
        self._redis = client
        self._limit = limit
        self._window = window_seconds

    async def allow(self, key: str) -> bool:
        now = int(time.time())
        bucket = f"rl:{key}:{now // self._window}"
        count = await self._redis.incr(bucket)
        if count == 1:
            await self._redis.expire(bucket, self._window)
        return bool(count <= self._limit)
