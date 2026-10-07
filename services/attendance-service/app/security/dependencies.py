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
    if principal.roles.isdisjoint({"admin", "teacher", "student"}):
        raise HTTPException(403, "A platform role is required.")
    return principal
