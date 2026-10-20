"""HTTP client with retries and circuit breaker (R-AI-10 pattern)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_seconds: float = 30.0
    failures: int = 0
    opened_at: float | None = field(default=None, init=False)

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.monotonic()

    def is_open(self) -> bool:
        if self.opened_at is None:
            return False
        if time.monotonic() - self.opened_at > self.recovery_seconds:
            self.opened_at = None
            self.failures = 0
            return False
        return True


class ResilientHttpClient:
    def __init__(self, breaker: CircuitBreaker | None = None) -> None:
        self._client = httpx.AsyncClient(timeout=30.0)
        self._breaker = breaker or CircuitBreaker()

    async def close(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=8))
    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if self._breaker.is_open():
            raise httpx.HTTPError("circuit open")
        try:
            response = await self._client.request(method, url, **kwargs)
            self._breaker.record_success()
            return response
        except httpx.HTTPError:
            self._breaker.record_failure()
            raise
