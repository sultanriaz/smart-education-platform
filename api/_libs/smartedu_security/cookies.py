from __future__ import annotations

from fastapi import Response

from .settings import SecuritySettings


def set_refresh_cookie(
    response: Response,
    refresh_token: str,
    settings: SecuritySettings,
) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_cookie_max_age_seconds,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
        path=settings.refresh_cookie_path,
    )


def clear_refresh_cookie(
    response: Response,
    settings: SecuritySettings,
) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        secure=settings.refresh_cookie_secure,
        httponly=True,
        samesite=settings.refresh_cookie_samesite,
    )
