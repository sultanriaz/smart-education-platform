from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.domain.models import DeliveryAttempt
from app.providers.email import EmailProvider, get_email_provider
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.notification_repository import NotificationRepository

MAX_ATTEMPTS = 3


class DeliveryService:
    def __init__(self, db: Session, provider: EmailProvider | None = None):
        self.db = db
        self.repo = DeliveryRepository(db)
        self.notifications = NotificationRepository(db)
        self.provider = provider or get_email_provider()

    def deliver(self, attempt_id: uuid.UUID) -> uuid.UUID | None:
        attempt = self.repo.get_attempt(attempt_id, for_update=True)
        if attempt is None:
            raise NotFoundError("Delivery attempt not found")
        if attempt.status != "PENDING":
            return None
        notification = self.notifications.get_notification(attempt.notification_id)
        if notification is None:
            raise NotFoundError("Notification not found")
        if attempt.channel == "IN_APP":
            attempt.status = "SENT" if notification.in_app_visible else "SKIPPED"
            self.db.commit()
            return None
        if attempt.channel != "EMAIL":
            attempt.status = "SKIPPED"
            attempt.last_error = "Unsupported channel"
            self.db.commit()
            return None
        if not notification.recipient_email:
            attempt.status = "SKIPPED"
            attempt.last_error = "Recipient email unavailable"
            self.db.commit()
            return None
        try:
            attempt.provider_message_id = self.provider.send(
                to_email=notification.recipient_email,
                subject=notification.title,
                body=notification.body,
            )
            attempt.status = "SENT"
            attempt.last_error = None
            self.db.commit()
            return None
        except Exception as exc:  # provider boundary
            attempt.status = "FAILED"
            attempt.last_error = str(exc)[:2000]
            retry_id = None
            if attempt.attempt_number < MAX_ATTEMPTS:
                retry = DeliveryAttempt(
                    notification_id=attempt.notification_id,
                    channel=attempt.channel,
                    status="PENDING",
                    attempt_number=attempt.attempt_number + 1,
                    next_attempt_at=datetime.now(UTC)
                    + timedelta(seconds=30 * (2 ** (attempt.attempt_number - 1))),
                )
                self.repo.add_attempt(retry)
                self.db.flush()
                retry_id = retry.id
            self.db.commit()
            return retry_id
