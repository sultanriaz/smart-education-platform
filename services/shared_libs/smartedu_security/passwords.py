from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL_LOCAL_RE = re.compile(r"^[^@]+")

COMMON_PASSWORDS = frozenset(
    {
        "password",
        "password123",
        "12345678",
        "123456789",
        "qwerty123",
        "admin123",
        "letmein123",
        "welcome123",
        "student123",
        "teacher123",
        "comsats123",
    }
)


@dataclass(frozen=True, slots=True)
class PasswordPolicy:
    min_length: int = 12
    max_length: int = 128
    require_upper: bool = True
    require_lower: bool = True
    require_digit: bool = True
    require_symbol: bool = True


class PasswordPolicyError(ValueError):
    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


def validate_password(
    password: str,
    *,
    email: str | None = None,
    full_name: str | None = None,
    policy: PasswordPolicy | None = None,
) -> None:
    policy = policy or PasswordPolicy()
    reasons: list[str] = []

    if len(password) < policy.min_length:
        reasons.append(f"password must contain at least {policy.min_length} characters")
    if len(password) > policy.max_length:
        reasons.append(f"password must contain at most {policy.max_length} characters")
    if policy.require_upper and not any(ch.isupper() for ch in password):
        reasons.append("password must contain an uppercase letter")
    if policy.require_lower and not any(ch.islower() for ch in password):
        reasons.append("password must contain a lowercase letter")
    if policy.require_digit and not any(ch.isdigit() for ch in password):
        reasons.append("password must contain a digit")
    if policy.require_symbol and not any(not ch.isalnum() for ch in password):
        reasons.append("password must contain a symbol")

    normalized = password.casefold()
    compact = re.sub(r"[^a-z0-9]", "", normalized)
    if normalized in COMMON_PASSWORDS or compact in COMMON_PASSWORDS:
        reasons.append("password is too common")

    if email:
        local = (_EMAIL_LOCAL_RE.match(email) or [None])[0]
        if isinstance(local, str):
            local_compact = re.sub(r"[^a-z0-9]", "", local.casefold())
            if len(local_compact) >= 4 and local_compact in compact:
                reasons.append("password must not contain the email identifier")

    if full_name:
        for token in re.findall(r"[A-Za-z0-9]+", full_name.casefold()):
            if len(token) >= 4 and token in normalized:
                reasons.append("password must not contain your name")
                break

    if reasons:
        raise PasswordPolicyError(reasons)
