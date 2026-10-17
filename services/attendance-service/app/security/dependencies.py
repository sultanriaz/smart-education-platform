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
        401, "Invalid or missing access token.", headers={"WWW-Authenticate": "Bearer"}
    )
    if credentials is None:
        raise unauthorized
    try:
        principal = verify_access_token(credentials.credentials)
    except KeyDiscoveryUnavailable as exc:
        raise HTTPException(503, "Identity verification keys are unavailable.") from exc
    except jwt.PyJWTError as exc:
        raise unauthorized from exc
    if "attendance.records.manage" in principal.permissions:
        live_permission(principal, "attendance.records.manage", get_settings().JWT_JWKS_URL)
    if principal.roles.isdisjoint({"admin", "teacher", "student"}):
        if not live_permission(principal, "attendance.records.manage", get_settings().JWT_JWKS_URL):
            raise HTTPException(403, "A platform role or attendance permission is required.")
    return principal
