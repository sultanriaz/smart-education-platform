from __future__ import annotations

import time
import uuid
from collections.abc import Iterable
from dataclasses import dataclass

import jwt
from fastapi import Header, HTTPException

from .constants import CORRELATION_ID_HEADER
from .context import ensure_correlation_id

ALGORITHM = "EdDSA"


@dataclass(frozen=True, slots=True)
class InternalPrincipal:
    service_name: str
    scopes: frozenset[str]
    correlation_id: str | None
    jti: str


class InternalTokenSigner:
    def __init__(
        self,
        *,
        service_name: str,
        private_key_pem: str,
        issuer: str = "smart-education-internal",
        ttl_seconds: int = 60,
    ):
        self.service_name = service_name
        self.private_key_pem = private_key_pem
        self.issuer = issuer
        self.ttl_seconds = ttl_seconds

    def issue(
        self,
        *,
        audience: str,
        scopes: Iterable[str] = (),
        correlation_id: str | None = None,
    ) -> str:
        now = int(time.time())
        cid = correlation_id or ensure_correlation_id()
        payload = {
            "iss": self.issuer,
            "sub": self.service_name,
            "aud": audience,
            "iat": now,
            "nbf": now - 1,
            "exp": now + self.ttl_seconds,
            "jti": str(uuid.uuid4()),
            "scope": sorted(set(scopes)),
            "correlation_id": cid,
            "token_type": "service",
        }
        return jwt.encode(payload, self.private_key_pem, algorithm=ALGORITHM)


class InternalTokenVerifier:
    def __init__(
        self,
        *,
        trusted_public_keys: dict[str, str],
        issuer: str = "smart-education-internal",
        leeway_seconds: int = 5,
    ):
        self.trusted_public_keys = trusted_public_keys
        self.issuer = issuer
        self.leeway_seconds = leeway_seconds

    def verify(
        self,
        token: str,
        *,
        audience: str,
        required_scopes: Iterable[str] = (),
    ) -> InternalPrincipal:
        unverified = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_aud": False,
            },
        )
        service_name = unverified.get("sub")
        if not isinstance(service_name, str) or service_name not in self.trusted_public_keys:
            raise ValueError("Untrusted internal service")

        claims = jwt.decode(
            token,
            self.trusted_public_keys[service_name],
            algorithms=[ALGORITHM],
            issuer=self.issuer,
            audience=audience,
            leeway=self.leeway_seconds,
            options={"require": ["iss", "sub", "aud", "iat", "exp", "jti", "token_type"]},
        )
        if claims.get("token_type") != "service":
            raise ValueError("Invalid internal token type")

        scopes = frozenset(value for value in claims.get("scope", []) if isinstance(value, str))
        missing = set(required_scopes) - scopes
        if missing:
            raise PermissionError(f"Missing internal scopes: {', '.join(sorted(missing))}")

        return InternalPrincipal(
            service_name=service_name,
            scopes=scopes,
            correlation_id=claims.get("correlation_id"),
            jti=str(claims["jti"]),
        )


def bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise ValueError("Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise ValueError("Expected Bearer token")
    return token


def internal_auth_dependency(
    verifier: InternalTokenVerifier,
    *,
    audience: str,
    required_scopes: Iterable[str] = (),
):
    required = tuple(required_scopes)

    async def dependency(
        authorization: str | None = Header(default=None),
        x_correlation_id: str | None = Header(
            default=None,
            alias=CORRELATION_ID_HEADER,
        ),
    ) -> InternalPrincipal:
        try:
            principal = verifier.verify(
                bearer_token(authorization),
                audience=audience,
                required_scopes=required,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=401,
                detail="Invalid internal service token",
            ) from exc

        if (
            principal.correlation_id
            and x_correlation_id
            and principal.correlation_id != x_correlation_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Internal token correlation_id does not match request header",
            )
        return principal

    return dependency
