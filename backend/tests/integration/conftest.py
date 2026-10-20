"""PostgreSQL integration fixtures (testcontainers)."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import AppConfig
from app.core.db.session import create_session_factory
from app.core.ids import Uuid7Generator
from app.modules.tenancy.infrastructure.repository import TenantRepository


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    try:
        from testcontainers.community.postgres import PostgresContainer
    except ImportError:
        pytest.skip("testcontainers not installed")
        return

    try:
        with PostgresContainer("postgres:16-alpine") as postgres:
            url = postgres.get_connection_url().replace("postgresql://", "postgresql+asyncpg://", 1)
            os.environ["DATABASE_URL"] = url
            os.environ["DATABASE_OWNER_URL"] = url
            rw_url = url.rsplit("@", 1)
            if len(rw_url) == 2:
                os.environ["DATABASE_RW_URL"] = (
                    "postgresql+asyncpg://app_rw:app_rw_dev_change_me@" + rw_url[1]
                )
            alembic_cfg = Config("alembic.ini")
            alembic_cfg.set_main_option("script_location", "migrations")
            command.upgrade(alembic_cfg, "head")
            yield url
    except Exception as exc:
        pytest.skip(f"Docker not available for integration tests: {exc}")


@pytest.fixture
async def pg_engine(postgres_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(postgres_url, pool_pre_ping=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def pg_session_factory(pg_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(pg_engine)


@pytest.fixture
def tenant_repo(pg_session_factory: async_sessionmaker[AsyncSession]) -> TenantRepository:
    return TenantRepository(pg_session_factory, Uuid7Generator())


@pytest.fixture
def pg_app_config(postgres_url: str) -> AppConfig:
    os.environ["APP_ENV"] = "test"
    os.environ["USE_IN_MEMORY_ADAPTERS"] = "false"
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["DATABASE_OWNER_URL"] = postgres_url
    return AppConfig()
