"""In-memory job queue for tests."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.core.jobs.ports import JobQueuePort


class InMemoryJobQueue(JobQueuePort):
    def __init__(self) -> None:
        self.jobs: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def enqueue(self, job_name: str, *args: Any, **kwargs: Any) -> str:
        job_id = str(uuid4())
        self.jobs.append((job_name, args, kwargs))
        return job_id
