"""Clock port (R-TEST-07)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime


class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime: ...

    @abstractmethod
    def utcnow(self) -> datetime: ...


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)

    def utcnow(self) -> datetime:
        return datetime.now(UTC)


class FixedClock(Clock):
    def __init__(self, fixed: datetime) -> None:
        self._fixed = fixed

    def now(self) -> datetime:
        return self._fixed

    def utcnow(self) -> datetime:
        return self._fixed
