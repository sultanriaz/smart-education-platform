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

    try:
        response = httpx.get(settings.JWT_JWKS_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        _jwks_cache = (now, data)
        return data
    except httpx.HTTPError:
        if (
            _jwks_cache
            and now - _jwks_cache[0]
            < settings.JWKS_CACHE_SECONDS + settings.JWKS_STALE_GRACE_SECONDS
        ):
            return _jwks_cache[1]
        raise


def current_principal(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> Principal:
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        jwks = _get_jwks()
        key_data = next(k for k in jwks["keys"] if k.get("kid") == header.get("kid"))
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=settings.JWT_ALGORITHMS,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={"require": ["exp", "iat", "sub", "iss", "aud", "jti"]},
        )

        if payload.get("type") != "access":
            raise ValueError("Wrong token type")

        user_id = uuid.UUID(payload["sub"])
        roles = {str(role).lower() for role in payload.get("roles", [])}
        if not roles.intersection({"admin", "teacher", "student"}):
            raise ValueError("Unsupported role")

        return Principal(user_id=user_id, roles=roles, token=token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc


def require_roles(*roles: str):
    required = {role.lower() for role in roles}

    def dependency(principal: Principal = Depends(current_principal)) -> Principal:
        if required.isdisjoint(principal.roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal

    return dependency


def require_internal_token(x_internal_token: str = Header(...)) -> None:
    if not secrets.compare_digest(x_internal_token, settings.INTERNAL_EVENT_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid internal token")
