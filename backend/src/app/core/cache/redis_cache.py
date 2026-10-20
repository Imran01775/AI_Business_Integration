"""Redis cache adapter with single-flight."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import redis.asyncio as redis

from app.core.cache.ports import CachePort


class RedisCache(CachePort):
    def __init__(self, client: redis.Redis) -> None:
        self._redis = client
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def get(self, key: str) -> bytes | None:
        value = await self._redis.get(key)
        if value is None:
            return None
        return value if isinstance(value, bytes) else value.encode()

    async def set(self, key: str, value: bytes, ttl_seconds: int | None = None) -> None:
        if ttl_seconds:
            await self._redis.set(key, value, ex=ttl_seconds)
        else:
            await self._redis.set(key, value)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def get_or_set(
        self,
        key: str,
        ttl_seconds: int | None,
        factory: Callable[[], Awaitable[bytes]],
    ) -> bytes:
        existing = await self.get(key)
        if existing is not None:
            return existing
        lock = self._lock_for(key)
        async with lock:
            existing = await self.get(key)
            if existing is not None:
                return existing
            value = await factory()
            await self.set(key, value, ttl_seconds)
            return value
