"""Alembic async environment (Phase 02)."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import AppConfig
from app.core.db.base import Base
from app.core.db.models import platform as _platform_models  # noqa: F401
from app.modules.audit.infrastructure import models as _audit_models  # noqa: F401
from app.modules.settings.infrastructure import models as _settings_models  # noqa: F401
from app.modules.tenancy.infrastructure import models as _tenancy_models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _database_url() -> str:
    cfg = AppConfig(_env_file=_BACKEND_ROOT / ".env")
    url = cfg.database_owner_url or cfg.database_url
    if not url:
        raise RuntimeError("DATABASE_OWNER_URL or DATABASE_URL must be set for migrations")
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _database_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
