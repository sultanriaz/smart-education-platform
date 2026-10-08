from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import EmailVerificationToken, PasswordResetToken


class SecurityTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def now() -> datetime:
        return datetime.now(UTC)

    def create_password_reset(
        self,
        *,
        user_id: uuid.UUID,
        token_digest: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        row = PasswordResetToken(
            user_id=user_id,
            token_digest=token_digest,
            expires_at=expires_at,
            created_at=self.now(),
        )
        self.db.add(row)
        self.db.flush()
        return row

    def create_email_verification(
        self,
        *,
        user_id: uuid.UUID,
        token_digest: str,
        expires_at: datetime,
    ) -> EmailVerificationToken:
        row = EmailVerificationToken(
            user_id=user_id,
            token_digest=token_digest,
            expires_at=expires_at,
            created_at=self.now(),
        )
        self.db.add(row)
        self.db.flush()
        return row

    def lock_password_reset(
        self,
        token_digest: str,
    ) -> PasswordResetToken | None:
        return self.db.scalar(
            select(PasswordResetToken)
            .where(PasswordResetToken.token_digest == token_digest)
            .with_for_update()
        )

    def lock_email_verification(
        self,
        token_digest: str,
    ) -> EmailVerificationToken | None:
        return self.db.scalar(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.token_digest == token_digest)
            .with_for_update()
        )

    def invalidate_password_resets(self, user_id: uuid.UUID) -> None:
        self.db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id))

    def invalidate_email_verifications(self, user_id: uuid.UUID) -> None:
        self.db.execute(
            delete(EmailVerificationToken).where(EmailVerificationToken.user_id == user_id)
        )
