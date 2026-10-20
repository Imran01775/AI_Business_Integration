"""ARQ worker settings stub (queues expanded in later phases)."""

from __future__ import annotations

from typing import ClassVar

from arq import cron
from arq.connections import RedisSettings

from app.core.config import AppConfig
from app.workers.outbox_relay import run_outbox_relay_once


async def outbox_relay_job(_ctx: dict[str, object]) -> int:
    return await run_outbox_relay_once()


_config = AppConfig()


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(str(_config.redis_url))
    functions: ClassVar[list[object]] = [outbox_relay_job]
    cron_jobs: ClassVar[list[object]] = [cron(outbox_relay_job, minute={0, 15, 30, 45})]  # type: ignore[arg-type]
