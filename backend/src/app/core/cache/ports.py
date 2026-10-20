"""Cache port (R-TEN-03)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class CachePort(ABC):
    @abstractmethod
    async def get(self, key: str) -> bytes | None: ...

    @abstractmethod
    async def set(self, key: str, value: bytes, ttl_seconds: int | None = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def get_or_set(
        self,
        key: str,
        ttl_seconds: int | None,
        factory: Any,
    ) -> bytes: ...


def versioned_key(
    tenant_id: UUID | None,
    module: str,
    entity: str,
    entity_id: str,
    version: int,
) -> str:
    tid = str(tenant_id) if tenant_id else "platform"
    return f"t:{tid}:{module}:{entity}:{entity_id}:v{version}"
