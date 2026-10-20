"""FastAPI exception handlers."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors.envelope import ErrorBody, ErrorEnvelope
from app.core.errors.exceptions import AppError
from app.core.logging.context import trace_id_var

logger = structlog.get_logger(__name__)


def _trace_id() -> str:
    return trace_id_var.get() or "unknown"


def envelope_response(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    body = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            details=details or {},
            trace_id=_trace_id(),
        ),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    logger.warning("app_error", code=exc.code, details=exc.details)
    return envelope_response(exc.http_status, exc.code, exc.message, exc.details)


async def validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return envelope_response(
        422,
        "common.validation_failed",
        "Request validation failed",
        {"errors": exc.errors()},
    )


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return envelope_response(exc.status_code, "common.http_error", str(exc.detail))


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", exc_info=exc)
    return envelope_response(500, "internal.unexpected", "An unexpected error occurred")
