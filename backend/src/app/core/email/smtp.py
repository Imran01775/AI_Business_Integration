"""SMTP email adapter (Mailpit in dev)."""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage as MimeEmail

from app.core.config import AppConfig
from app.core.email.ports import EmailMessage, EmailSenderPort


class SmtpEmailSender(EmailSenderPort):
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    async def send(self, message: EmailMessage) -> None:
        def _send() -> None:
            mime = MimeEmail()
            mime["From"] = self._config.smtp_from
            mime["To"] = message.to
            mime["Subject"] = message.subject
            mime.set_content(message.body_text)
            if message.body_html:
                mime.add_alternative(message.body_html, subtype="html")
            with smtplib.SMTP(self._config.smtp_host, self._config.smtp_port) as smtp:
                if self._config.smtp_use_tls:
                    smtp.starttls()
                smtp.send_message(mime)

        await asyncio.to_thread(_send)
