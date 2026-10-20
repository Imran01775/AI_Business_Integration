"""ID generation port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from uuid6 import uuid7


class IdGenerator(ABC):
    @abstractmethod
    def uuid7(self) -> UUID: ...


class Uuid7Generator(IdGenerator):
    def uuid7(self) -> UUID:
        return uuid7()
