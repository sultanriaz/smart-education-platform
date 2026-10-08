"""Use Identity-owned models and the existing Argon2 password path."""

from datetime import UTC, datetime

from sqlalchemy import update

from app.domain.entities.outbox import OutboxEvent
from app.domain.entities.refresh_token import RefreshToken
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password
from app.sprint18 import security_settings
from app.sprint18_security.contracts import AccountSnapshot
from app.sprint18_security.event_payloads import encrypted_security_notification_data


class AccountAdapter:
    def __init__(self, db):
        self.db = db
        self.users = UserRepository(db)

    @staticmethod
    def snapshot(user):
        if user is None:
            return None
        return AccountSnapshot(
            user.id, user.email, user.full_name, user.is_active, user.is_verified
        )

    def find_by_email(self, email):
        return self.snapshot(self.users.get_by_email(email))

    def get_by_id(self, user_id):
        return self.snapshot(self.users.get_by_id(user_id))

    def update_password(self, user_id, plaintext_password):
        self.users.get_by_id(user_id).password_hash = hash_password(plaintext_password)

    def mark_email_verified(self, user_id):
        self.users.get_by_id(user_id).is_verified = True

    def revoke_refresh_tokens(self, user_id):
        self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )


class SecurityAuditAdapter:
    def __init__(self, db):
        self.repo = AuditRepository(db)

    def record(self, *, event_type, user_id, metadata):
        self.repo.record(action=event_type, user_id=user_id, details=metadata)


class SecurityNotificationAdapter:
    def __init__(self, db):
        self.db = db

    def queue(self, event_type, user_id, email, token):
        self.db.add(
            OutboxEvent(
                event_type=event_type,
                aggregate_id=user_id,
                payload=encrypted_security_notification_data(
                    event_type=event_type, email=email, token=token, settings=security_settings()
                ),
            )
        )

    def queue_password_reset(self, *, user_id, email, token, expires_in_seconds):
        self.queue("identity.password_reset.requested", user_id, email, token)

    def queue_email_verification(self, *, user_id, email, token, expires_in_seconds):
        self.queue("identity.email_verification.requested", user_id, email, token)
