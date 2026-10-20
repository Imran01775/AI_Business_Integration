"""Tenancy workspace routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.core.auth.dependencies import require_permission, require_principal, resolve_tenant
from app.core.errors.exceptions import PermissionDeniedError
from app.core.logging.context import trace_id_var
from app.modules.tenancy.api.schemas import (
    AcceptInvitationRequest,
    ChangeRoleRequest,
    CreateTenantRequest,
    InviteMemberRequest,
    TenantResponse,
)
from app.modules.tenancy.application.facade import TenancyFacade
from app.modules.tenancy.infrastructure.repositories import TenancyRepository
from app.modules.tenancy.permissions import PERM_TEAM_INVITE_AGENT, PERM_TEAM_MANAGE
from app.shared.principal import Principal

router = APIRouter(prefix="/api/v1", tags=["tenancy"])


async def require_team_invite(
    principal: Annotated[Principal, Depends(resolve_tenant)],
) -> Principal:
    if principal.has_permission(PERM_TEAM_MANAGE) or principal.has_permission(PERM_TEAM_INVITE_AGENT):
        return principal
    raise PermissionDeniedError(details={"permission": "team:invite"})



def _tenancy(request: Request) -> TenancyFacade:
    return request.app.state.container.tenancy


def _repo(request: Request) -> TenancyRepository:
    return request.app.state.container.tenancy_repo


@router.get("/me/workspaces")
async def list_workspaces(
    principal: Annotated[Principal, Depends(require_principal)],
    request: Request,
) -> dict[str, list[TenantResponse]]:
    rows = await _repo(request).list_memberships_for_user(principal.user_id)
    return {
        "data": [
            TenantResponse(
                id=str(membership.tenant_id),
                slug=tenant.slug,
                display_name=tenant.display_name,
                role=membership.role,
            )
            for membership, tenant in rows
        ]
    }


@router.post("/tenants", status_code=201)
async def create_tenant(
    body: CreateTenantRequest,
    principal: Annotated[Principal, Depends(require_principal)],
    request: Request,
) -> dict[str, str]:
    tenant_id = await _tenancy(request).create_tenant(
        owner_user_id=principal.user_id,
        display_name=body.display_name,
        slug=body.slug,
        timezone=body.timezone,
        locale=body.locale,
        currency=body.currency,
        trace_id=trace_id_var.get(),
    )
    return {"id": str(tenant_id)}


@router.post("/tenants/{tenant_id}/invitations", status_code=204)
async def invite_member(
    tenant_id: str,
    body: InviteMemberRequest,
    principal: Annotated[Principal, Depends(require_team_invite)],
    request: Request,
) -> None:
    if str(principal.tenant_id) != tenant_id:
        raise PermissionDeniedError(details={"reason": "tenant_mismatch"})
    if principal.tenant_role == "manager" and body.role != "agent":
        raise PermissionDeniedError(details={"reason": "manager_invite_agent_only"})
    if body.role != "agent" and not principal.has_permission(PERM_TEAM_MANAGE):
        raise PermissionDeniedError()
    if body.role == "agent" and not (
        principal.has_permission(PERM_TEAM_MANAGE) or principal.has_permission(PERM_TEAM_INVITE_AGENT)
    ):
        raise PermissionDeniedError()
    await _tenancy(request).invite_member(
        tenant_id=UUID(tenant_id),
        email=body.email,
        role=body.role,
        invited_by=principal.user_id,
        locale="en",
        trace_id=trace_id_var.get(),
    )


@router.post("/invitations/accept")
async def accept_invitation(
    body: AcceptInvitationRequest,
    principal: Annotated[Principal, Depends(require_principal)],
    request: Request,
) -> dict[str, str]:
    email = await request.app.state.container.identity.get_user_email(principal.user_id)
    tenant_id = await _tenancy(request).accept_invitation(
        body.token,
        principal.user_id,
        email,
        trace_id_var.get(),
    )
    return {"tenant_id": str(tenant_id)}


@router.patch("/tenants/{tenant_id}/members/{user_id}/role")
async def change_role(
    tenant_id: str,
    user_id: str,
    body: ChangeRoleRequest,
    principal: Annotated[Principal, Depends(require_permission(PERM_TEAM_MANAGE))],
    request: Request,
) -> dict[str, str]:
    membership = await _repo(request).change_role(
        UUID(tenant_id),
        UUID(user_id),
        body.role,
        principal.user_id,
    )
    return {"role": membership.role}


@router.delete("/tenants/{tenant_id}/members/{user_id}", status_code=204)
async def remove_member(
    tenant_id: str,
    user_id: str,
    principal: Annotated[Principal, Depends(require_permission(PERM_TEAM_MANAGE))],
    request: Request,
) -> None:
    await _repo(request).remove_member(UUID(tenant_id), UUID(user_id), principal.user_id)
