"""Identity API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=256)
    locale: str = Field(default="en", max_length=8)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str
    device_name: str | None = Field(default=None, max_length=256)
    client_type: str = Field(default="web", pattern="^(web|mobile)$")


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str | None = None


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    locale: str = "en"


class PasswordResetConfirm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str


class SessionItem(BaseModel):
    id: str
    client_type: str
    device_name: str | None
    ip_address: str | None
    last_seen_at: str
    created_at: str
    is_current: bool


class SessionsResponse(BaseModel):
    data: list[SessionItem]
