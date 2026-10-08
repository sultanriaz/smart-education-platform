from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from smartedu_contracts import EventEnvelope
from smartedu_security import decrypt_sensitive_json


@dataclass(frozen=True, slots=True)
class SecurityEmail:
    recipient: str
    subject: str
    body: str


def _frontend_link(base_url: str, path: str, token: str) -> str:
    """
    Put the one-time token in the URL fragment, not query string.

    Fragments are not sent to the frontend web server in the HTTP request,
    reducing exposure in HTTP access logs and referrer URLs.
    """
    base = base_url.rstrip("/")
    return f"{base}{path}#token={quote(token, safe='')}"


def security_email_from_event(
    envelope: EventEnvelope,
    *,
    frontend_public_url: str,
    encryption_key: str,
) -> SecurityEmail:
    encrypted = envelope.data.get("encrypted_payload")
    if not isinstance(encrypted, str):
        raise ValueError("Security event is missing encrypted_payload")

    data = decrypt_sensitive_json(
        encrypted,
        key=encryption_key,
        purpose=envelope.event_type,
    )
    email = data.get("email")
    token = data.get("token")

    if not isinstance(email, str) or not isinstance(token, str):
        raise ValueError("Decrypted security event is missing recipient/token")

    if envelope.event_type == "identity.password_reset.requested":
        link = _frontend_link(
            frontend_public_url,
            "/reset-password",
            token,
        )
        return SecurityEmail(
            recipient=email,
            subject="Reset your Smart Education password",
            body=(
                "A password reset was requested for your account. "
                f"Open this link to continue: {link}\n\n"
                "If you did not request this, you can ignore this message."
            ),
        )

    if envelope.event_type == "identity.email_verification.requested":
        link = _frontend_link(
            frontend_public_url,
            "/verify-email",
            token,
        )
        return SecurityEmail(
            recipient=email,
            subject="Verify your Smart Education email",
            body=(f"Verify your email address to complete account setup: {link}"),
        )

    raise ValueError(f"Unsupported security event: {envelope.event_type}")
