from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    user_id: uuid.UUID
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool


class IdentityAccountAdapter(Protocol):
    def find_by_email(self, email: str) -> AccountSnapshot | None: ...
    def get_by_id(self, user_id: uuid.UUID) -> AccountSnapshot | None: ...

    def update_password(
        self,
        user_id: uuid.UUID,
        plaintext_password: str,
    ) -> None: ...

    def mark_email_verified(self, user_id: uuid.UUID) -> None: ...

    def revoke_refresh_tokens(self, user_id: uuid.UUID) -> None: ...


class IdentitySecurityNotificationSink(Protocol):
    """
    Implement this by writing to Identity's transactional outbox.

    Before an event is persisted, encrypt `{email, token}` with
    `encrypt_sensitive_json(...)` and store only `data.encrypted_payload`.
    Never persist the plaintext token/email pair in an outbox row or log.
    """

    def queue_password_reset(
        self,
        *,
        user_id: uuid.UUID,
        email: str,
        token: str,
        expires_in_seconds: int,
    ) -> None: ...

    def queue_email_verification(
        self,
        *,
        user_id: uuid.UUID,
        email: str,
        token: str,
        expires_in_seconds: int,
    ) -> None: ...


class SecurityAuditSink(Protocol):
    def record(
        self,
        *,
        event_type: str,
        user_id: uuid.UUID | None,
        metadata: dict[str, object],
    ) -> None: ...
