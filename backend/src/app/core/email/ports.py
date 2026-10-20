"""Email sender port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmailMessage:
    to: str
    subject: str
    body_text: str
    body_html: str | None = None


class EmailSenderPort(ABC):
    @abstractmethod
    async def send(self, message: EmailMessage) -> None: ...
