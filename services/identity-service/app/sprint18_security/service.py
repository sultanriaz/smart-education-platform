from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from smartedu_security import (
    PasswordPolicy,
    SecuritySettings,
    hash_token,
    issue_one_time_token,
    validate_password,
)
from smartedu_security.security_events import (
    EMAIL_VERIFICATION_REQUESTED,
    EMAIL_VERIFIED,
    PASSWORD_RESET_COMPLETED,
    PASSWORD_RESET_REQUESTED,
    SESSIONS_REVOKED,
)
from sqlalchemy.orm import Session

from .contracts import (
    IdentityAccountAdapter,
    IdentitySecurityNotificationSink,
    SecurityAuditSink,
)
from .repository import SecurityTokenRepository


class SecurityFlowError(ValueError):
    pass


class InvalidOrExpiredToken(SecurityFlowError):
    pass


class IdentitySecurityService:
    def __init__(
        self,
        *,
        db: Session,
        accounts: IdentityAccountAdapter,
        notifications: IdentitySecurityNotificationSink,
        audit: SecurityAuditSink,
        settings: SecuritySettings,
    ):
        self.db = db
        self.accounts = accounts
        self.notifications = notifications
        self.audit = audit
        self.settings = settings
        self.tokens = SecurityTokenRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _redacted_email_hash(email: str) -> str:
        return hashlib.sha256(email.strip().casefold().encode()).hexdigest()

    def request_password_reset(self, email: str) -> None:
        normalized = email.strip().casefold()
        account = self.accounts.find_by_email(normalized)

        # The caller always receives the same generic response. If no eligible
        # account exists, do no token work and return silently.
        if account is None or not account.is_active:
            self.audit.record(
                event_type=PASSWORD_RESET_REQUESTED,
                user_id=None,
                metadata={
                    "eligible_account": False,
                    "email_hash": self._redacted_email_hash(normalized),
                },
            )
            self.db.commit()
            return

        token = issue_one_time_token(
            ttl_seconds=self.settings.password_reset_ttl_seconds,
            pepper=self.settings.security_token_pepper,
        )

        self.tokens.invalidate_password_resets(account.user_id)
        self.tokens.create_password_reset(
            user_id=account.user_id,
            token_digest=token.digest,
            expires_at=token.expires_at,
        )

        self.notifications.queue_password_reset(
            user_id=account.user_id,
            email=account.email,
            token=token.plaintext,
            expires_in_seconds=self.settings.password_reset_ttl_seconds,
        )
        self.audit.record(
            event_type=PASSWORD_RESET_REQUESTED,
            user_id=account.user_id,
            metadata={"eligible_account": True},
        )
        self.db.commit()

    def reset_password(self, *, token: str, new_password: str) -> None:
        digest = hash_token(
            token,
            pepper=self.settings.security_token_pepper,
        )
        row = self.tokens.lock_password_reset(digest)
        now = self._now()

        if row is None or row.used_at is not None or row.expires_at.replace(tzinfo=UTC) <= now:
            raise InvalidOrExpiredToken("Invalid or expired password-reset token")

        account = self.accounts.get_by_id(row.user_id)
        if account is None or not account.is_active:
            raise InvalidOrExpiredToken("Invalid or expired password-reset token")

        validate_password(
            new_password,
            email=account.email,
            full_name=account.full_name,
            policy=PasswordPolicy(
                min_length=self.settings.password_min_length,
                max_length=self.settings.password_max_length,
            ),
        )

        self.accounts.update_password(account.user_id, new_password)
        self.accounts.revoke_refresh_tokens(account.user_id)
        self.tokens.invalidate_password_resets(account.user_id)

        self.audit.record(
            event_type=PASSWORD_RESET_COMPLETED,
            user_id=account.user_id,
            metadata={},
        )
        self.audit.record(
            event_type=SESSIONS_REVOKED,
            user_id=account.user_id,
            metadata={"reason": "password_reset"},
        )
        self.db.commit()

    def request_email_verification(self, email: str) -> None:
        normalized = email.strip().casefold()
        account = self.accounts.find_by_email(normalized)

        if account is None or not account.is_active or account.is_verified:
            self.audit.record(
                event_type=EMAIL_VERIFICATION_REQUESTED,
                user_id=account.user_id if account else None,
                metadata={
                    "eligible_account": False,
                    "email_hash": self._redacted_email_hash(normalized),
                },
            )
            self.db.commit()
            return

        token = issue_one_time_token(
            ttl_seconds=self.settings.email_verification_ttl_seconds,
            pepper=self.settings.security_token_pepper,
        )
        self.tokens.invalidate_email_verifications(account.user_id)
        self.tokens.create_email_verification(
            user_id=account.user_id,
            token_digest=token.digest,
            expires_at=token.expires_at,
        )

        self.notifications.queue_email_verification(
            user_id=account.user_id,
            email=account.email,
            token=token.plaintext,
            expires_in_seconds=self.settings.email_verification_ttl_seconds,
        )
        self.audit.record(
            event_type=EMAIL_VERIFICATION_REQUESTED,
            user_id=account.user_id,
            metadata={"eligible_account": True},
        )
        self.db.commit()

    def confirm_email_verification(self, token: str) -> None:
        digest = hash_token(
            token,
            pepper=self.settings.security_token_pepper,
        )
        row = self.tokens.lock_email_verification(digest)
        now = self._now()

        if row is None or row.used_at is not None or row.expires_at.replace(tzinfo=UTC) <= now:
            raise InvalidOrExpiredToken("Invalid or expired verification token")

        account = self.accounts.get_by_id(row.user_id)
        if account is None or not account.is_active:
            raise InvalidOrExpiredToken("Invalid or expired verification token")

        self.accounts.mark_email_verified(account.user_id)
        self.tokens.invalidate_email_verifications(account.user_id)
        self.audit.record(
            event_type=EMAIL_VERIFIED,
            user_id=account.user_id,
            metadata={},
        )
        self.db.commit()
