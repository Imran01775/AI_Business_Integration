"""JWT access tokens (claims per doc 06)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from app.core.config import AppConfig
from app.core.errors.exceptions import UnauthenticatedError


class JwtService:
    def __init__(self, config: AppConfig) -> None:
        self._secret = config.jwt_secret
        self._algorithm = config.jwt_algorithm
        self._ttl_seconds = config.jwt_access_token_ttl_seconds

    def encode_access_token(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        token_version: int,
        platform_roles: list[str],
        tenant_id: UUID | None = None,
        tenant_role: str | None = None,
    ) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "sid": str(session_id),
            "ver": token_version,
            "roles": platform_roles,
            "iat": now,
            "exp": now + timedelta(seconds=self._ttl_seconds),
        }
        if tenant_id is not None:
            payload["ten"] = str(tenant_id)
        if tenant_role is not None:
            payload["trole"] = tenant_role
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"require": ["exp", "sub", "sid", "ver"]},
            )
        except jwt.PyJWTError as exc:
            raise UnauthenticatedError(details={"reason": str(exc)}) from exc
