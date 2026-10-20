"""Settings module ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class SettingDefinitionRow(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "setting_definitions"

    key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    chain: Mapped[str] = mapped_column(String(16), nullable=False)
    value_type: Mapped[str] = mapped_column(String(32), nullable=False)
    default_value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    schema: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    overridable_at: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    bounded_by: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    edit_permission: Mapped[str] = mapped_column(String(128), nullable=False)
    entitlement: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_secret: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")


class SettingValueRow(Base, UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin):
    __tablename__ = "setting_values"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "scope_layer",
            "scope_id",
            "key",
            name="uq_setting_values_scope_key",
        ),
    )

    tenant_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    scope_layer: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class SettingValueHistoryRow(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "setting_values_history"

    tenant_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    scope_layer: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    changed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class MessageTemplateRow(Base, UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin):
    __tablename__ = "message_templates"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "key", "locale", name="uq_message_templates_tenant_key_locale"
        ),
    )

    tenant_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    locale: Mapped[str] = mapped_column(String(8), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")


class MessageTemplateHistoryRow(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "message_templates_history"

    tenant_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    locale: Mapped[str] = mapped_column(String(8), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class SecretRow(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "secrets"
    __table_args__ = (
        UniqueConstraint("tenant_id", "scope_type", "scope_id", "key", name="uq_secrets_scope_key"),
    )

    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(64), nullable=False)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    ciphertext: Mapped[bytes] = mapped_column(nullable=False)
    key_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
