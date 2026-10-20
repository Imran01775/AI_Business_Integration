"""ARQ job queue adapter (ADR 0003)."""

from __future__ import annotations

from typing import Any

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import AppConfig
from app.core.jobs.ports import JobQueuePort


class ArqJobQueue(JobQueuePort):
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    @classmethod
    async def create(cls, config: AppConfig) -> ArqJobQueue:
        redis_settings = RedisSettings.from_dsn(str(config.redis_url))
        pool = await create_pool(redis_settings)
        return cls(pool)

    async def enqueue(self, job_name: str, *args: Any, **kwargs: Any) -> str:
        job = await self._pool.enqueue_job(job_name, *args, **kwargs)
        return job.job_id if job else ""
