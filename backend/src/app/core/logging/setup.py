"""Structlog JSON logging configuration."""

from __future__ import annotations

import logging
import sys

import structlog

from app.core.logging.context import (
    module_var,
    request_id_var,
    tenant_id_var,
    trace_id_var,
    user_id_var,
)
from app.core.logging.redaction import redaction_processor


def _add_contextvars(
    _logger: object,
    _method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
    if trace_id_var.get():
        event_dict["trace_id"] = trace_id_var.get()
    if request_id_var.get():
        event_dict["request_id"] = request_id_var.get()
    if tenant_id_var.get():
        event_dict["tenant_id"] = tenant_id_var.get()
    if user_id_var.get():
        event_dict["user_id"] = user_id_var.get()
    if module_var.get():
        event_dict["module"] = module_var.get()
    return event_dict


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        _add_contextvars,  # type: ignore[list-item]
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        redaction_processor,  # type: ignore[list-item]
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
