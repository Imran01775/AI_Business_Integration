"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.auth.dependencies import require_principal
from app.core.config import AppConfig
from app.core.errors.exceptions import AppError
from app.core.errors.handlers import (
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from app.core.logging.setup import configure_logging
from app.core.observability.glitchtip import init_glitchtip
from app.core.observability.metrics import metrics_endpoint
from app.core.observability.otel import instrument_fastapi, setup_otel
from app.core.realtime.sse import build_sse_router
from app.main.container import AppContainer, build_container, shutdown_container
from app.main.middleware import (
    BodySizeLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from app.main.routes.health import router as health_router
from app.modules.identity.api.me_router import router as me_router
from app.modules.identity.api.router import router as auth_router
from app.modules.public.api.router import router as public_router
from app.modules.tenancy.api.router import router as tenancy_router


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    container: AppContainer = app.state.container
    await shutdown_container(container)


def create_app(config: AppConfig | None = None) -> FastAPI:
    app_config = config or AppConfig()
    configure_logging(debug=app_config.app_debug)
    init_glitchtip(app_config)
    container = build_container(app_config)

    app = FastAPI(
        title="AI Sales Agent API",
        version="0.1.0",
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
        lifespan=_lifespan,
    )
    app.state.container = container

    setup_otel(app_config, container.engine)
    instrument_fastapi(app)

    app.add_middleware(BodySizeLimitMiddleware, max_bytes=app_config.max_request_body_bytes)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=500)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if app_config.app_env.value == "production":
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(health_router)
    app.include_router(public_router)
    app.include_router(auth_router)
    app.include_router(me_router)
    app.include_router(tenancy_router)
    app.include_router(
        build_sse_router(lambda: container.redis),
        dependencies=[Depends(require_principal)],
    )
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)

    return app
