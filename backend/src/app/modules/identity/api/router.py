"""Identity auth routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response

from app.core.auth.dependencies import (
    COOKIE_REFRESH,
    require_principal,
)
from app.core.logging.context import trace_id_var
from app.core.ratelimit import RateLimiter
from app.main.container import AppContainer
from app.modules.identity.api.cookies import clear_auth_cookies, set_auth_cookies
from app.modules.identity.api.schemas import (
    AuthResponse,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    SessionItem,
    SessionsResponse,
    VerifyEmailRequest,
)
from app.modules.identity.application.facade import IdentityFacade
from app.shared.principal import Principal

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _container(request: Request) -> AppContainer:
    return request.app.state.container


def _identity(request: Request) -> IdentityFacade:
    return request.app.state.container.identity


async def _auth_rate_limit(request: Request) -> None:
    container = _container(request)
    limiter = RateLimiter(container.redis, limit=20, window_seconds=60)
    ip = request.client.host if request.client else "unknown"
    if not await limiter.allow(f"auth:{ip}"):
        from app.core.errors.exceptions import RateLimitedError

        raise RateLimitedError()


@router.post("/register", status_code=201, dependencies=[Depends(_auth_rate_limit)])
async def register(body: RegisterRequest, request: Request) -> dict[str, str]:
    identity = _identity(request)
    user_id = await identity.register(
        email=body.email,
        password=body.password,
        display_name=body.display_name,
        locale=body.locale,
        trace_id=trace_id_var.get(),
    )
    return {"user_id": str(user_id)}


@router.post("/verify-email", dependencies=[Depends(_auth_rate_limit)])
async def verify_email(body: VerifyEmailRequest, request: Request) -> dict[str, str]:
    identity = _identity(request)
    user_id = await identity.verify_email(body.token, trace_id_var.get())
    return {"user_id": str(user_id)}


@router.post("/login", dependencies=[Depends(_auth_rate_limit)])
async def login(body: LoginRequest, request: Request, response: Response) -> AuthResponse:
    identity = _identity(request)
    config = _container(request).config
    result = await identity.login(
        email=body.email,
        password=body.password,
        client_type=body.client_type,  # type: ignore[arg-type]
        device_name=body.device_name,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        trace_id=trace_id_var.get(),
    )
    if body.client_type == "web":
        set_auth_cookies(
            response,
            config,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            csrf_token=result.csrf_token,
        )
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        user_id=str(result.user_id),
    )


@router.post("/refresh", dependencies=[Depends(_auth_rate_limit)])
async def refresh(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    refresh_cookie: Annotated[str | None, Cookie(alias=COOKIE_REFRESH)] = None,
) -> AuthResponse:
    identity = _identity(request)
    config = _container(request).config
    token = (body.refresh_token if body else None) or refresh_cookie
    if not token:
        from app.core.errors.exceptions import UnauthenticatedError

        raise UnauthenticatedError()
    result = await identity.refresh(token, trace_id_var.get())
    client_type = request.headers.get("X-Client", "web")
    if client_type == "web" or refresh_cookie:
        set_auth_cookies(
            response,
            config,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            csrf_token=None,
        )
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        user_id=str(result.user_id),
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    principal: Annotated[Principal, Depends(require_principal)],
    all_sessions: bool = False,
) -> Response:
    identity = _identity(request)
    await identity.logout(principal.user_id, principal.session_id, trace_id_var.get(), all_sessions)
    clear_auth_cookies(response, _container(request).config)
    return Response(status_code=204)


@router.post("/password-reset/request", dependencies=[Depends(_auth_rate_limit)])
async def password_reset_request(body: PasswordResetRequest, request: Request) -> Response:
    await _identity(request).request_password_reset(body.email, body.locale)
    return Response(status_code=204)


@router.post("/password-reset/confirm", dependencies=[Depends(_auth_rate_limit)])
async def password_reset_confirm(body: PasswordResetConfirm, request: Request) -> Response:
    await _identity(request).reset_password(body.token, body.new_password, trace_id_var.get())
    return Response(status_code=204)


@router.get("/sessions")
async def list_sessions(
    principal: Annotated[Principal, Depends(require_principal)],
    request: Request,
) -> SessionsResponse:
    rows = await _identity(request).list_sessions(principal.user_id, principal.session_id)
    return SessionsResponse(
        data=[
            SessionItem(
                id=str(r.id),
                client_type=r.client_type,
                device_name=r.device_name,
                ip_address=r.ip_address,
                last_seen_at=r.last_seen_at.isoformat(),
                created_at=r.created_at.isoformat(),
                is_current=r.is_current,
            )
            for r in rows
        ]
    )


@router.delete("/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: str,
    principal: Annotated[Principal, Depends(require_principal)],
    request: Request,
) -> Response:
    from uuid import UUID

    await _identity(request).revoke_session(principal.user_id, UUID(session_id), trace_id_var.get())
    return Response(status_code=204)
