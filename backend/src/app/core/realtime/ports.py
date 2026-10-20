"""Realtime publisher port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RealtimePublisherPort(ABC):
    @abstractmethod
    async def publish(self, channel: str, payload: dict[str, Any]) -> None: ...
