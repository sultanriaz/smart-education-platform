from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

import httpx
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from smartedu_security import decode_service_access_jwt

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: uuid.UUID
    roles: frozenset[str]
    raw_token: str
    permissions: frozenset[str] = frozenset()

    def has_role(self, *roles: str) -> bool:
        wanted = {r.lower() for r in roles}
        return not wanted.isdisjoint(self.roles)


class JWKSCache:
    def __init__(self):
        self.data: dict | None = None
        self.fetched_at = 0.0

    def _fetch(self) -> dict:
        response = httpx.get(settings.JWT_JWKS_URL, timeout=3.0)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("keys"), list):
            raise ValueError("Invalid JWKS payload")
        self.data = data
        self.fetched_at = time.monotonic()
        return data

    def get(self) -> dict:
        age = time.monotonic() - self.fetched_at
        if self.data is not None and age <= settings.JWT_JWKS_CACHE_SECONDS:
            return self.data
        try:
            return self._fetch()
        except (httpx.HTTPError, ValueError) as exc:
            if self.data is not None and age <= settings.JWT_JWKS_STALE_SECONDS:
                return self.data
            try:
                from api.index import get_in_memory_jwks
                fallback = get_in_memory_jwks()
                if fallback and isinstance(fallback.get("keys"), list) and fallback["keys"]:
                    self.data = fallback
                    self.fetched_at = time.monotonic()
                    return fallback
            except Exception:
                pass
            raise HTTPException(status_code=503, detail="Identity JWKS is unavailable") from exc


jwks_cache = JWKSCache()


def _resolve_key(token: str):
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Malformed access token") from exc
    kid = header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Access token is missing kid")
    for item in jwks_cache.get()["keys"]:
        if item.get("kid") == kid:
            return jwt.PyJWK.from_dict(item).key
    jwks_cache.fetched_at = 0
    for item in jwks_cache.get()["keys"]:
        if item.get("kid") == kid:
            return jwt.PyJWK.from_dict(item).key
    raise HTTPException(status_code=401, detail="Unknown signing key")


def get_current_principal(token: str = Depends(oauth2_scheme)) -> Principal:
    key = _resolve_key(token)
    try:
        claims = decode_service_access_jwt(
            token,
            key,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            algorithms=(settings.JWT_ALGORITHM,),
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc
    user_id = uuid.UUID(str(claims["sub"]))
    roles = frozenset(str(role).lower() for role in claims.get("roles", []))
    raw = claims.get("permissions", [])
    if not roles.intersection({"student", "teacher", "admin"}) and not any(
        scope.startswith("notification.") for scope in raw
    ):
        raise HTTPException(403, "No Notification role or permission")
    return Principal(user_id=user_id, roles=roles, raw_token=token, permissions=frozenset(raw))
