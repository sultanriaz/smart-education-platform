"""Wave 13/14 deterministic, bounded security helpers."""
import hashlib
import json

from app.core.errors import ConflictError

SENSITIVE = {"password", "password_hash", "token", "access_token", "refresh_token", "authorization", "cookie", "secret", "api_key", "reset_token"}


def redact(value, depth=0):
    if depth > 12:
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(key)[:128]: ("[REDACTED]" if any(part in str(key).lower() for part in SENSITIVE) else redact(item, depth + 1)) for key, item in list(value.items())[:500]}
    if isinstance(value, (tuple, list)):
        return [redact(item, depth + 1) for item in value[:500]]
    if isinstance(value, str):
        return value[:4096].replace("\r", " ").replace("\n", " ")
    return value if isinstance(value, (int, float, bool)) or value is None else "[REDACTED]"


def digest_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def assert_version(current, expected):
    if expected is not None and expected != current:
        raise ConflictError(f"Revision conflict: expected {expected}, current {current}")


def stable_bucket(flag_key: str, user_id: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{flag_key}:{user_id}".encode()).digest()[:8], "big") % 10000


def feature_enabled(flag, user_id):
    if not flag.enabled:
        return False
    percent = (flag.config or {}).get("percentage", 100)
    if type(percent) not in (int, float) or not 0 <= percent <= 100:
        return False
    return stable_bucket(flag.key, str(user_id)) < int(percent * 100)
