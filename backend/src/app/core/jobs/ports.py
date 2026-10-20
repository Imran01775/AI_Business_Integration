"""Background job queue port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JobQueuePort(ABC):
    @abstractmethod
    async def enqueue(self, job_name: str, *args: Any, **kwargs: Any) -> str: ...
