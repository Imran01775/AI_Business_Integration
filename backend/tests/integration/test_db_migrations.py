"""Alembic upgrade/downgrade for Phase 02 schema."""

from __future__ import annotations

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.integration
@pytest.mark.asyncio
async def test_migrations_upgrade_head(pg_engine: AsyncEngine, postgres_url: str) -> None:
    async with pg_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT to_regclass('public.tenants'), to_regclass('public.secrets')"),
        )
        tenants, secrets = result.one()
        assert tenants is not None
        assert secrets is not None


@pytest.mark.integration
def test_migrations_downgrade_and_upgrade(postgres_url: str) -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "migrations")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
