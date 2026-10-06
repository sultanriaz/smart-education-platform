from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.jwt import KeyDiscoveryUnavailable, Principal, verify_access_token

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
        return verify_access_token(credentials.credentials)
    except KeyDiscoveryUnavailable as exc:
        raise HTTPException(503, "Identity verification keys are unavailable.") from exc
    except jwt.PyJWTError as exc:
        raise unauthorized from exc


def require_admin(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
    if not principal.is_admin:
        raise HTTPException(403, "Administrator role required.")
    return principal


def require_staff(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
    if principal.roles.isdisjoint({"admin", "teacher"}):
        raise HTTPException(403, "Administrator or teacher role required.")
    return principal
