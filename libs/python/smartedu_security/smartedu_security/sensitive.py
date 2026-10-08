from __future__ import annotations

import base64
import json
import os
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SensitivePayloadError(ValueError):
    pass


def generate_encryption_key() -> str:
    return base64.urlsafe_b64encode(AESGCM.generate_key(bit_length=256)).decode()


def _decode_key(value: str) -> bytes:
    try:
        key = base64.urlsafe_b64decode(value.encode())
    except Exception as exc:
        raise SensitivePayloadError("Encryption key is not valid base64") from exc
    if len(key) != 32:
        raise SensitivePayloadError("Encryption key must decode to 32 bytes")
    return key


def encrypt_sensitive_json(
    payload: dict[str, Any],
    *,
    key: str,
    purpose: str,
) -> str:
    nonce = os.urandom(12)
    plaintext = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    aad = purpose.encode()
    ciphertext = AESGCM(_decode_key(key)).encrypt(nonce, plaintext, aad)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt_sensitive_json(
    value: str,
    *,
    key: str,
    purpose: str,
) -> dict[str, Any]:
    try:
        raw = base64.urlsafe_b64decode(value.encode())
        nonce, ciphertext = raw[:12], raw[12:]
        plaintext = AESGCM(_decode_key(key)).decrypt(
            nonce,
            ciphertext,
            purpose.encode(),
        )
        payload = json.loads(plaintext)
    except Exception as exc:
        raise SensitivePayloadError("Sensitive payload could not be decrypted") from exc

    if not isinstance(payload, dict):
        raise SensitivePayloadError("Sensitive payload must decode to an object")
    return payload
