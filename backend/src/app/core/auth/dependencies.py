"""FastAPI auth / tenant / permission dependencies."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth.secure_token import hash_token
from app.core.errors.exceptions import PermissionDeniedError, UnauthenticatedError
from app.main.container import AppContainer
from app.modules.identity.application.facade import IdentityFacade
from app.modules.tenancy.infrastructure.repositories import TenancyRepository
from app.shared.principal import Principal
from app.shared.rbac import permissions_for_platform_roles, permissions_for_tenant_role

_bearer = HTTPBearer(auto_error=False)

COOKIE_ACCESS = "access_token"
COOKIE_REFRESH = "refresh_token"
COOKIE_CSRF = "csrf_token"
HEADER_CSRF = "X-CSRF-Token"


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def get_identity(container: AppContainer = Depends(get_container)) -> IdentityFacade:
    return container.identity


def get_tenancy_repo(container: AppContainer = Depends(get_container)) -> TenancyRepository:
    return container.tenancy_repo


async def resolve_principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    access_cookie: Annotated[str | None, Cookie(alias=COOKIE_ACCESS)] = None,
    identity: IdentityFacade = Depends(get_identity),
) -> Principal:
    jwt = request.app.state.container.jwt
    token: str | None = None
    auth_method = "bearer"
    if credentials is not None and credentials.credentials:
        token = credentials.credentials
        auth_method = "bearer"
    elif access_cookie:
        token = access_cookie
        auth_method = "cookie"
    if not token:
        raise UnauthenticatedError()

    claims = jwt.decode_access_token(token)
    user_id = UUID(claims["sub"])
    session_id = UUID(claims["sid"])
    token_version = int(claims["ver"])
    await identity.validate_access_token_session(user_id, session_id, token_version)

    platform_roles = frozenset(claims.get("roles") or [])
    tenant_id = UUID(claims["ten"]) if claims.get("ten") else None
    tenant_role = claims.get("trole")

    permissions = permissions_for_platform_roles(platform_roles)
    if tenant_role:
        permissions = permissions | permissions_for_tenant_role(tenant_role)

    return Principal(
        user_id=user_id,
        session_id=session_id,
        email="",
        token_version=token_version,
        platform_roles=platform_roles,
        tenant_id=tenant_id,
        tenant_role=tenant_role,
        permissions=permissions,
        auth_method=auth_method,
    )


async def require_principal(
    principal: Annotated[Principal, Depends(resolve_principal)],
) -> Principal:
    return principal


async def require_csrf_for_cookie(
    request: Request,
    principal: Annotated[Principal, Depends(require_principal)],
    csrf_header: Annotated[str | None, Header(alias=HEADER_CSRF)] = None,
    csrf_cookie: Annotated[str | None, Cookie(alias=COOKIE_CSRF)] = None,
    identity: IdentityFacade = Depends(get_identity),
) -> Principal:
    if principal.auth_method != "cookie":
        return principal
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return principal
    if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
        raise PermissionDeniedError(details={"reason": "csrf"})
    csrf_hash = await identity.session_csrf_hash(principal.session_id)
    if csrf_hash is None or csrf_hash != hash_token(csrf_cookie):
        raise PermissionDeniedError(details={"reason": "csrf"})
    return principal


async def resolve_tenant(
    principal: Annotated[Principal, Depends(require_csrf_for_cookie)],
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-Id")] = None,
    tenancy_repo: TenancyRepository = Depends(get_tenancy_repo),
) -> Principal:
    if not x_tenant_id:
        raise PermissionDeniedError(details={"reason": "tenant_required"})
    tenant_id = UUID(x_tenant_id)
    membership = await tenancy_repo.get_membership(tenant_id, principal.user_id)
    if membership is None:
        raise PermissionDeniedError(details={"reason": "not_a_member"})
    permissions = principal.permissions | permissions_for_tenant_role(membership.role)
    return Principal(
        user_id=principal.user_id,
        session_id=principal.session_id,
        email=principal.email,
        token_version=principal.token_version,
        platform_roles=principal.platform_roles,
        tenant_id=tenant_id,
        tenant_role=membership.role,
        permissions=permissions,
        auth_method=principal.auth_method,
    )


def require_permission(permission: str):
    async def _check(principal: Annotated[Principal, Depends(resolve_tenant)]) -> Principal:
        if not principal.has_permission(permission):
            raise PermissionDeniedError(details={"permission": permission})
        return principal

    return _check


def require_platform_role(role: str):
    async def _check(principal: Annotated[Principal, Depends(require_principal)]) -> Principal:
        if not principal.has_platform_role(role):
            raise PermissionDeniedError(details={"platform_role": role})
        return principal

    return _check
