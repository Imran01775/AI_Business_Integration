"""Settings persistence ports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.modules.settings.domain.definitions import ScopeLayer


@dataclass(frozen=True, slots=True)
class TemplateDetail:
    body: str
    variables: list[str]
    version: int
    locale: str
    updated_at: datetime


class SettingValueStorePort(ABC):
    @abstractmethod
    async def get_value(
        self,
        layer: ScopeLayer,
        scope_id: str | None,
        key: str,
        *,
        rls_tenant_id: UUID | None = None,
    ) -> Any | None: ...

    @abstractmethod
    async def set_value(
        self,
        layer: ScopeLayer,
        scope_id: str | None,
        key: str,
        value: Any,
        *,
        rls_tenant_id: UUID | None = None,
        changed_by: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def rollback_value(
        self,
        layer: ScopeLayer,
        scope_id: str | None,
        key: str,
        to_version: int,
        *,
        rls_tenant_id: UUID | None = None,
        changed_by: str | None = None,
    ) -> None: ...


class TemplateStorePort(ABC):
    @abstractmethod
    async def upsert(
        self,
        key: str,
        locale: str,
        body: str,
        variables: list[str],
        *,
        tenant_id: UUID | None = None,
    ) -> int: ...

    @abstractmethod
    async def get_template(
        self,
        key: str,
        locale: str,
        *,
        tenant_id: UUID | None = None,
    ) -> tuple[str, list[str]] | None: ...

    @abstractmethod
    async def get_template_detail(
        self,
        key: str,
        locale: str,
        *,
        tenant_id: UUID | None = None,
    ) -> TemplateDetail | None: ...

    @abstractmethod
    async def rollback(
        self,
        key: str,
        locale: str,
        to_version: int,
        *,
        tenant_id: UUID | None = None,
    ) -> None: ...


class SecretsStorePort(ABC):
    @abstractmethod
    async def put_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        plaintext: str,
        *,
        tenant_id: UUID,
    ) -> None: ...

    @abstractmethod
    async def has_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> bool: ...

    @abstractmethod
    async def get_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> str: ...


class EntitlementCheckerPort(ABC):
    @abstractmethod
    async def has_entitlement(self, entitlement: str, tenant_id: str | None) -> bool: ...
