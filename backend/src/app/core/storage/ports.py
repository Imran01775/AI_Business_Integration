"""Object storage port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PresignedUrl:
    url: str
    expires_in_seconds: int


class ObjectStoragePort(ABC):
    @abstractmethod
    async def put_bytes(self, key: str, data: bytes, content_type: str) -> None: ...

    @abstractmethod
    async def get_bytes(self, key: str) -> bytes: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def presigned_get(self, key: str, expires_seconds: int = 3600) -> PresignedUrl: ...
