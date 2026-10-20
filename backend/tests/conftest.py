"""Shared pytest fixtures."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("USE_IN_MEMORY_ADAPTERS", "true")

from app.core.config import AppConfig
from app.main.app_factory import create_app


@pytest.fixture
def app_config() -> AppConfig:
    return AppConfig()


@pytest.fixture
def test_client(app_config: AppConfig):
    from fastapi.testclient import TestClient

    app = create_app(app_config)
    with TestClient(app) as client:
        yield client
