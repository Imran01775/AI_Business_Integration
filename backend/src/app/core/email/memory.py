"""In-memory email capture for tests."""

from __future__ import annotations

from app.core.email.ports import EmailMessage, EmailSenderPort


class InMemoryEmailSender(EmailSenderPort):
    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> None:
        self.sent.append(message)
