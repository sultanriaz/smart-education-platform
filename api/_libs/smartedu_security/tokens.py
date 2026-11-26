from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class OneTimeToken:
    plaintext: str
    digest: str
    expires_at: datetime


def hash_token(token: str, *, pepper: str = "") -> str:
    key = pepper.encode()
    data = token.encode()
    if key:
        return hmac.new(key, data, hashlib.sha256).hexdigest()
    return hashlib.sha256(data).hexdigest()


def issue_one_time_token(
    *,
    ttl_seconds: int,
    pepper: str = "",
    now: datetime | None = None,
) -> OneTimeToken:
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        raise ValueError("Token clock must be timezone-aware")
    raw = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    return OneTimeToken(
        plaintext=raw,
        digest=hash_token(raw, pepper=pepper),
        expires_at=current + timedelta(seconds=ttl_seconds),
    )


def constant_time_token_match(
    plaintext: str,
    expected_digest: str,
    *,
    pepper: str = "",
) -> bool:
    return hmac.compare_digest(
        hash_token(plaintext, pepper=pepper),
        expected_digest,
    )
