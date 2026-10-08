from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

import httpx
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer = HTTPBearer(auto_error=True)
_jwks_cache: tuple[float, dict] | None = None


@dataclass(frozen=True)
class Principal:
    user_id: uuid.UUID
    roles: set[str]
    token: str


def _jwks() -> dict:
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
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> Principal:
    token = creds.credentials
    try:
        header = jwt.get_unverified_header(token)
        jwks = _jwks()
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
            raise ValueError("wrong token type")
        user_id = uuid.UUID(payload["sub"])
        roles = {str(x).lower() for x in payload.get("roles", [])}
        if not roles.intersection({"admin", "teacher", "student"}):
            raise ValueError("unsupported role")
        return Principal(user_id=user_id, roles=roles, token=token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc


def require_roles(*roles: str):
    expected = {r.lower() for r in roles}

    def dep(p: Principal = Depends(current_principal)) -> Principal:
        if expected.isdisjoint(p.roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return p

    return dep
