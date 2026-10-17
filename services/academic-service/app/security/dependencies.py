from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.jwt import KeyDiscoveryUnavailable, Principal, verify_access_token
from smartedu_security.live_permissions import live_permission
from app.core.config import get_settings

bearer = HTTPBearer(auto_error=False)


def get_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Principal:
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or missing access token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        principal = verify_access_token(credentials.credentials)
        if "admin" not in principal.roles:
            for scope in ("academic.records.read", "academic.records.write"):
                if scope in principal.permissions:
                    live_permission(principal, scope, get_settings().JWT_JWKS_URL)
        if not principal.roles.intersection({"admin", "teacher", "student"}) and not (
            principal.permissions & {"academic.records.read", "academic.records.write"}
        ):
            raise HTTPException(403, "No Academic role or permission")
        return principal
    except KeyDiscoveryUnavailable as exc:
        raise HTTPException(503, "Identity verification keys are unavailable.") from exc
    except jwt.PyJWTError as exc:
        raise unauthorized from exc


def _permit(principal: Principal, scope: str) -> bool:
    return live_permission(principal, scope, get_settings().JWT_JWKS_URL)


def require_admin(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
    if not principal.is_admin and not _permit(principal, "academic.records.write"):
        raise HTTPException(403, "Administrator role or academic write permission required.")
    return principal


def require_admin_read(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
    if not principal.is_admin and not (_permit(principal, "academic.records.read")
                                       or _permit(principal, "academic.records.write")):
        raise HTTPException(403, "Academic read permission required.")
    return principal


def require_staff(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
    if principal.roles.isdisjoint({"admin", "teacher"}) and not (
        _permit(principal, "academic.records.read")
        or _permit(principal, "academic.records.write")
    ):
        raise HTTPException(403, "Academic staff/read permission required.")
    return principal
