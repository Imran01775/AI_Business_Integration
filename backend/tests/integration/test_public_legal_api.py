"""Public legal document API."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import AppConfig
from app.main.app_factory import create_app


@pytest.fixture
async def test_app(pg_app_config: AppConfig) -> object:
    pg_app_config.use_in_memory_adapters = True
    app = create_app(pg_app_config)
    from app.main.seed.defaults import seed_default_templates

    await seed_default_templates(app.state.container.template_store)
    return app


@pytest.mark.integration
async def test_legal_privacy_en(test_app: object) -> None:
    transport = ASGITransport(app=test_app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/public/legal/privacy", params={"locale": "en"})
        assert res.status_code == 200
        body = res.json()
        assert body["document"] == "privacy"
        assert body["version"] >= 1
        assert "Privacy Policy" in body["body_html"]
