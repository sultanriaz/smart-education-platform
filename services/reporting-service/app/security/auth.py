from __future__ import annotations

import secrets
import time
import uuid
from dataclasses import dataclass

import httpx
import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer = HTTPBearer(auto_error=True)
_jwks_cache: tuple[float, dict] | None = None


@dataclass(frozen=True)
class Principal:
    user_id: uuid.UUID
    roles: set[str]
    token: str


def _get_jwks() -> dict:
    global _jwks_cache
    now = time.time()
    if _jwks_cache and now - _jwks_cache[0] < settings.JWKS_CACHE_SECONDS:
        return _jwks_cache[1]

    response = httpx.get(settings.JWT_JWKS_URL, timeout=5)
    response.raise_for_status()
    data = response.json()
    _jwks_cache = (now, data)
    return data


def current_principal(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> Principal:
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        jwks = _get_jwks()
        key_data = next(k for k in jwks["keys"] if k.get("kid") == header.get("kid"))
        key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
        payload = jwt.decode(
            token,
            key,
            algorithms=settings.JWT_ALGORITHMS,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={"require": ["exp", "iat", "sub", "iss", "aud", "jti"]},
        )
        if payload.get("type") != "access":
            raise ValueError("Wrong token type")
        roles = {str(role).lower() for role in payload.get("roles", [])}
        return Principal(user_id=uuid.UUID(payload["sub"]), roles=roles, token=token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc


def require_roles(*roles: str):
    required = {r.lower() for r in roles}

    def dependency(principal: Principal = Depends(current_principal)):
        if required.isdisjoint(principal.roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal

    return dependency


def require_internal_token(x_internal_token: str = Header(...)) -> None:
    if not secrets.compare_digest(x_internal_token, settings.INTERNAL_EVENT_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid internal token")
