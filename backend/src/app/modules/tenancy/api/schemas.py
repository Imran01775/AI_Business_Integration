"""Tenancy API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateTenantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1, max_length=256)
    slug: str | None = Field(default=None, max_length=64)
    timezone: str = Field(default="UTC", max_length=64)
    locale: str = Field(default="en", max_length=8)
    currency: str = Field(default="BDT", min_length=3, max_length=3)


class TenantResponse(BaseModel):
    id: str
    slug: str
    display_name: str
    role: str


class InviteMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    role: str = Field(pattern="^(manager|agent)$")


class AcceptInvitationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str


class ChangeRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    role: str = Field(pattern="^(owner|manager|agent)$")
