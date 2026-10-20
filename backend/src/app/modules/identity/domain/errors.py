"""Identity domain errors."""

from __future__ import annotations

from app.core.errors.exceptions import AppError, ConflictError, DomainRuleViolation, NotFoundError


class EmailAlreadyRegisteredError(ConflictError):
    code = "identity.email_already_registered"
    message_key = "errors.identity.email_already_registered"


class InvalidCredentialsError(DomainRuleViolation):
    code = "identity.invalid_credentials"
    message_key = "errors.identity.invalid_credentials"


class EmailNotVerifiedError(DomainRuleViolation):
    code = "identity.email_not_verified"
    message_key = "errors.identity.email_not_verified"


class InvalidVerificationTokenError(DomainRuleViolation):
    code = "identity.invalid_verification_token"
    message_key = "errors.identity.invalid_verification_token"


class InvalidResetTokenError(DomainRuleViolation):
    code = "identity.invalid_reset_token"
    message_key = "errors.identity.invalid_reset_token"


class RefreshTokenReuseError(AppError):
    code = "identity.refresh_token_reuse"
    http_status = 401
    message_key = "errors.identity.refresh_token_reuse"


class SessionNotFoundError(NotFoundError):
    code = "identity.session_not_found"
    message_key = "errors.identity.session_not_found"
