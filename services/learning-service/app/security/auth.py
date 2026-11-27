from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from smartedu_security import decode_service_access_jwt
from smartedu_security.live_permissions import live_permission

from app.core.config import settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    user_id: uuid.UUID
    roles: frozenset[str]
    raw_token: str
    permissions: frozenset[str] = frozenset()


class JWKSCache:
    def __init__(self):
        self._keys: dict[str, Any] = {}
        self._expires_at = 0.0

    def _fetch(self) -> dict[str, Any]:
        try:
            response = httpx.get(settings.JWT_JWKS_URL, timeout=5.0)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            if self._keys and time.time() < self._expires_at:
                return self._keys
            raise HTTPException(status_code=503, detail="Identity JWKS unavailable") from exc

        keys: dict[str, Any] = {}
        for item in data.get("keys", []):
            kid = item.get("kid")
            if kid:
                keys[kid] = jwt.PyJWK.from_dict(item).key
        if not keys:
            raise HTTPException(status_code=503, detail="Identity JWKS contained no usable keys")
        self._keys = keys
        self._expires_at = time.time() + settings.JWT_JWKS_CACHE_TTL_SECONDS
        return keys

    def get_key(self, kid: str):
        if time.time() >= self._expires_at or kid not in self._keys:
            self._fetch()
        key = self._keys.get(kid)
        if key is None:
            self._fetch()
            key = self._keys.get(kid)
        if key is None:
            raise HTTPException(status_code=401, detail="Unknown signing key")
        return key


jwks_cache = JWKSCache()


def verify_token(token: str) -> Principal:
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        alg = header.get("alg")
        if not kid or alg not in settings.JWT_ALGORITHMS:
            raise HTTPException(status_code=401, detail="Unsupported token")
        key = jwks_cache.get_key(kid)
        payload = decode_service_access_jwt(
            token,
            key,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            algorithms=settings.JWT_ALGORITHMS,
        )
        user_id = uuid.UUID(str(payload["sub"]))
        # Built-in roles are case-sensitive. Never promote "Admin" to "admin".
        roles = frozenset(payload.get("roles", []))
        permissions = frozenset(payload.get("permissions", []))
        if roles.isdisjoint({"admin", "teacher", "student"}) and permissions.isdisjoint(
            {"learning.resources.manage", "learning.categories.manage"}
        ):
            raise HTTPException(403, "No Learning role or permission")
        return Principal(user_id=user_id, roles=roles, raw_token=token, permissions=permissions)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc


def get_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    principal = verify_token(credentials.credentials)
    if "learning.resources.manage" in principal.permissions:
        live_permission(principal, "learning.resources.manage", settings.JWT_JWKS_URL)
    elif "learning.categories.manage" in principal.permissions:
        live_permission(principal, "learning.categories.manage", settings.JWT_JWKS_URL)
    if not principal.roles.intersection({"admin", "teacher", "student"}) and not principal.permissions.intersection(
        {"learning.resources.manage", "learning.categories.manage"}
    ):
        raise HTTPException(403, "No Learning role or permission")
    return principal


def require_roles(*required: str):
    required_set = {x.lower() for x in required}

    def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.roles.isdisjoint(required_set):
            scope = ("learning.categories.manage" if required_set == {"admin"}
                     else "learning.resources.manage" if "teacher" in required_set else None)
            if not scope or not live_permission(principal, scope, settings.JWT_JWKS_URL):
                raise HTTPException(403, "Insufficient permissions")
        return principal

    return dependency
