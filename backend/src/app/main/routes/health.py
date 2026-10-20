"""Health probes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(request: Request) -> JSONResponse:
    container = request.app.state.container
    checks: dict[str, Any] = {}
    ok = True
    try:
        async with container.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        ok = False
        checks["database"] = str(exc)
    try:
        await container.redis.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        ok = False
        checks["redis"] = str(exc)
    status_code = 200 if ok else 503
    return JSONResponse(
        status_code=status_code, content={"status": "ok" if ok else "degraded", "checks": checks}
    )
