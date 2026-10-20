from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import AppConfig
from app.core.errors.exceptions import NotFoundError
from app.main.app_factory import create_app


def test_health_live_and_metrics() -> None:
    app = create_app(AppConfig(app_env="test", use_in_memory_adapters=True))
    with TestClient(app) as client:
        live = client.get("/health/live")
        assert live.status_code == 200
        metrics = client.get("/metrics")
        assert metrics.status_code == 200
        assert b"python_info" in metrics.content or len(metrics.content) > 0


def test_error_envelope_has_trace_id() -> None:
    app = create_app(AppConfig(app_env="test", use_in_memory_adapters=True))

    @app.get("/missing")
    async def missing() -> None:
        raise NotFoundError("gone")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/missing")
        assert response.status_code == 404
        body = response.json()
        assert "error" in body
        assert body["error"]["trace_id"]
        assert response.headers.get("X-Trace-Id")
