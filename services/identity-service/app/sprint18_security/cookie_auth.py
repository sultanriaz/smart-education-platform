from __future__ import annotations

from fastapi import HTTPException, Request, Response, status
from smartedu_security import (
    SecuritySettings,
    clear_refresh_cookie,
    require_trusted_origin,
    set_refresh_cookie,
)


def public_access_token_payload(
    access_token: str,
    *,
    token_type: str = "bearer",
    expires_in: int | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "access_token": access_token,
        "token_type": token_type,
    }
    if expires_in is not None:
        payload["expires_in"] = expires_in
    return payload


def set_browser_refresh_cookie(
    response: Response,
    refresh_token: str,
    settings: SecuritySettings,
) -> None:
    set_refresh_cookie(response, refresh_token, settings)


def refresh_token_from_cookie(
    request: Request,
    settings: SecuritySettings,
) -> str:
    require_trusted_origin(request, settings.frontend_origins)
    value = request.cookies.get(settings.refresh_cookie_name)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session is unavailable",
        )
    return value


def clear_browser_refresh_cookie(
    response: Response,
    settings: SecuritySettings,
) -> None:
    clear_refresh_cookie(response, settings)
