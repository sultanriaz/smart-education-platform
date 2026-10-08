from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "password",
        "new_password",
        "confirm_password",
        "access_token",
        "refresh_token",
        "token",
        "secret",
        "private_key",
        "api_key",
        "encrypted_payload",
    }
)


def redact_mapping(
    value: Mapping[str, Any],
    *,
    replacement: str = "[REDACTED]",
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in value.items():
        if key.casefold() in SENSITIVE_KEYS:
            result[key] = replacement
        elif isinstance(item, Mapping):
            result[key] = redact_mapping(item, replacement=replacement)
        elif isinstance(item, list):
            result[key] = [
                redact_mapping(entry, replacement=replacement)
                if isinstance(entry, Mapping)
                else entry
                for entry in item
            ]
        else:
            result[key] = item
    return result
