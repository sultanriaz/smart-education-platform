from __future__ import annotations

from smartedu_security import SecuritySettings, enforce_new_password


def enforce_registration_password(
    *,
    password: str,
    email: str,
    full_name: str | None,
    settings: SecuritySettings,
) -> None:
    enforce_new_password(
        password,
        email=email,
        full_name=full_name,
        min_length=settings.password_min_length,
        max_length=settings.password_max_length,
    )
