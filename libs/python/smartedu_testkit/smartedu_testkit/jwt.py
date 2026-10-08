from __future__ import annotations

import base64
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


@dataclass
class JwtTestIssuer:
    issuer: str = "smart-education-identity"
    audience: str = "smart-education-platform"

    def __post_init__(self) -> None:
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.kid = "test-key-1"
        self.jwk = {
            "kty": "OKP",
            "crv": "Ed25519",
            "x": _b64url(public_bytes),
            "kid": self.kid,
            "use": "sig",
            "alg": "EdDSA",
        }

    def jwks(self) -> dict:
        return {"keys": [self.jwk]}

    def token(
        self,
        *,
        subject: uuid.UUID,
        roles: Iterable[str],
        expires_in_seconds: int = 900,
        now: datetime | None = None,
        token_type: str = "access",
        extra: dict | None = None,
    ) -> str:
        now = now or datetime.now(UTC)
        payload = {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": str(subject),
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
            "type": token_type,
            "roles": list(roles),
            "jti": str(uuid.uuid4()),
        }
        payload.update(extra or {})
        return jwt.encode(
            payload,
            self.private_key,
            algorithm="EdDSA",
            headers={"kid": self.kid},
        )
