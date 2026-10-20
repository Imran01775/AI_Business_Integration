"""Async SQLAlchemy engine factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import AppConfig


def create_engine(config: AppConfig) -> AsyncEngine:
    return create_async_engine(
        str(config.database_url),
        echo=config.app_debug and config.app_env.value == "development",
        pool_pre_ping=True,
    )
