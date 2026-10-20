"""In-memory cache for tests."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from app.core.cache.ports import CachePort


class InMemoryCache(CachePort):
    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def get(self, key: str) -> bytes | None:
        return self._data.get(key)

    async def set(self, key: str, value: bytes, ttl_seconds: int | None = None) -> None:
        _ = ttl_seconds
        self._data[key] = value

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

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
