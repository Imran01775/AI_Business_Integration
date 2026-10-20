"""Typed application errors (R-OBS-02, doc 04 §6)."""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base error with stable code and HTTP mapping."""

    code: str = "internal.unexpected"
    http_status: int = 500
    message_key: str = "errors.internal.unexpected"
    retryable: bool = False

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
        code: str | None = None,
    ) -> None:
        self.message = message or self.code
        self.details = details or {}
        if code is not None:
            self.code = code
        super().__init__(self.message)


class ValidationError(AppError):
    code = "common.validation_failed"
    http_status = 422
    message_key = "errors.common.validation_failed"


class NotFoundError(AppError):
    code = "common.not_found"
    http_status = 404
    message_key = "errors.common.not_found"


class PermissionDeniedError(AppError):
    code = "common.permission_denied"
    http_status = 403
    message_key = "errors.common.permission_denied"


class UnauthenticatedError(AppError):
    code = "common.unauthenticated"
    http_status = 401
    message_key = "errors.common.unauthenticated"


class ConflictError(AppError):
    code = "common.conflict"
    http_status = 409
    message_key = "errors.common.conflict"


class QuotaExceededError(AppError):
    code = "usage.quota_exceeded"
    http_status = 429
    message_key = "errors.usage.quota_exceeded"


class RateLimitedError(AppError):
    code = "common.rate_limited"
    http_status = 429
    message_key = "errors.common.rate_limited"


class ExternalProviderError(AppError):
    code = "common.external_provider"
    http_status = 502
    message_key = "errors.common.external_provider"
    retryable = True


class DomainRuleViolation(AppError):  # noqa: N818 — catalogue name from doc 04
    code = "common.domain_rule_violation"
    http_status = 422
    message_key = "errors.common.domain_rule_violation"
