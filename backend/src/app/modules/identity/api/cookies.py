"""Auth cookie helpers."""

from __future__ import annotations

from fastapi import Response

from app.core.auth.dependencies import COOKIE_ACCESS, COOKIE_CSRF, COOKIE_REFRESH
from app.core.config import AppConfig


def set_auth_cookies(
    response: Response,
    config: AppConfig,
    *,
    access_token: str,
    refresh_token: str,
    csrf_token: str | None,
) -> None:
    common = {
        "httponly": True,
        "secure": config.auth_cookie_secure,
        "samesite": "lax",
        "path": "/",
    }
    if config.auth_cookie_domain:
        common["domain"] = config.auth_cookie_domain
    response.set_cookie(COOKIE_ACCESS, access_token, max_age=config.jwt_access_token_ttl_seconds, **common)
    response.set_cookie(
        COOKIE_REFRESH,
        refresh_token,
        max_age=config.jwt_refresh_token_ttl_days * 86400,
        **common,
    )
    if csrf_token is not None:
        response.set_cookie(
            COOKIE_CSRF,
            csrf_token,
            max_age=config.jwt_refresh_token_ttl_days * 86400,
            httponly=False,
            secure=config.auth_cookie_secure,
            samesite="lax",
            path="/",
            domain=config.auth_cookie_domain,
        )


def clear_auth_cookies(response: Response, config: AppConfig) -> None:
    for name in (COOKIE_ACCESS, COOKIE_REFRESH, COOKIE_CSRF):
        response.delete_cookie(name, path="/", domain=config.auth_cookie_domain)
