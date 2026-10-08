from __future__ import annotations

import logging
import smtplib
import uuid
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailProvider(Protocol):
    def send(self, *, to_email: str, subject: str, body: str) -> str: ...


class ConsoleEmailProvider:
    def send(self, *, to_email: str, subject: str, body: str) -> str:
        message_id = f"console-{uuid.uuid4()}"
        logger.info("Development email prepared: message_id=%s", message_id)
        return message_id


@dataclass(slots=True)
class SMTPEmailProvider:
    host: str = settings.SMTP_HOST
    port: int = settings.SMTP_PORT

    def send(self, *, to_email: str, subject: str, body: str) -> str:
        message = EmailMessage()
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
            smtp.send_message(message)
        return message.get("Message-ID") or f"smtp-{uuid.uuid4()}"


def get_email_provider() -> EmailProvider:
    if settings.EMAIL_PROVIDER.lower() == "smtp":
        return SMTPEmailProvider()
    return ConsoleEmailProvider()
