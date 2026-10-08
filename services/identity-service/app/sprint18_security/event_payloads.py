from __future__ import annotations

from smartedu_security import SecuritySettings, encrypt_sensitive_json


def encrypted_security_notification_data(
    *,
    event_type: str,
    email: str,
    token: str,
    settings: SecuritySettings,
) -> dict[str, str]:
    """
    Produce the only payload that may be written to the Identity outbox for
    password-reset/email-verification delivery.
    """
    if not settings.security_notification_encryption_key:
        raise RuntimeError("SECURITY_NOTIFICATION_ENCRYPTION_KEY is required")

    encrypted = encrypt_sensitive_json(
        {"email": email, "token": token},
        key=settings.security_notification_encryption_key,
        purpose=event_type,
    )
    return {"encrypted_payload": encrypted}
