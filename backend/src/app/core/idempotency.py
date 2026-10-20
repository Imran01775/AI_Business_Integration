"""Idempotency-Key handling (R-API-06)."""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis
from fastapi import Request


class IdempotencyStore:
    def __init__(self, client: redis.Redis, ttl_seconds: int = 86400) -> None:
        self._redis = client
        self._ttl = ttl_seconds

    def _key(self, tenant: str, idempotency_key: str) -> str:
        return f"idempotency:{tenant}:{idempotency_key}"

    async def get_cached_response(
        self,
        tenant: str,
        idempotency_key: str,
    ) -> tuple[int, dict[str, Any]] | None:
        raw = await self._redis.get(self._key(tenant, idempotency_key))
        if not raw:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode()
        data = json.loads(raw)
        return int(data["status"]), data["body"]

    async def store_response(
        self,
        tenant: str,
        idempotency_key: str,
        status: int,
        body: dict[str, Any],
    ) -> None:
        payload = json.dumps({"status": status, "body": body})
        await self._redis.set(self._key(tenant, idempotency_key), payload, ex=self._ttl)


async def idempotency_dependency(request: Request) -> str | None:
    return request.headers.get("Idempotency-Key")
