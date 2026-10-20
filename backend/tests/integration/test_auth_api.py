"""Auth API: bearer + cookie + CSRF."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import AppConfig
from app.main.app_factory import create_app


@pytest.fixture
async def test_app(pg_app_config: AppConfig, postgres_url: str) -> object:
    pg_app_config.use_in_memory_adapters = True
    app = create_app(pg_app_config)
    from app.main.seed.defaults import seed_default_templates

    await seed_default_templates(app.state.container.template_store)
    return app


@pytest.mark.integration
async def test_register_verify_login_bearer(test_app: object) -> None:
    transport = ASGITransport(app=test_app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "flow@example.com",
                "password": "Password123!",
                "display_name": "Flow User",
                "locale": "en",
            },
        )
        assert reg.status_code == 201
        from app.core.email.memory import InMemoryEmailSender

        container = test_app.state.container  # type: ignore[attr-defined]
        assert isinstance(container.email, InMemoryEmailSender)
        verify_body = container.email.sent[-1].body_text
        token = verify_body.split("token=")[-1].strip()
        verify = await client.post("/api/v1/auth/verify-email", json={"token": token})
        assert verify.status_code == 200
        login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "flow@example.com",
                "password": "Password123!",
                "client_type": "mobile",
            },
        )
        assert login.status_code == 200
        access = login.json()["access_token"]
        me = await client.get(
            "/api/v1/me/settings",
            headers={"Authorization": f"Bearer {access}"},
        )
        assert me.status_code == 200
        assert "user.locale" in me.json()["values"]
