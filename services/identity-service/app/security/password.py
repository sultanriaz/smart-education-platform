import hashlib
import hmac
import os
import secrets

try:
    from pwdlib import PasswordHash
    _password_hash = PasswordHash.recommended()
except Exception:
    _password_hash = None


def hash_password(password: str) -> str:
    if _password_hash is not None:
        try:
            return _password_hash.hash(password)
        except Exception:
            pass
    # Built-in PBKDF2-HMAC-SHA256 fallback
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"pbkdf2:sha256:100000${salt}${key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("pbkdf2:sha256:"):
        try:
            parts = password_hash.split("$")
            salt = parts[1]
            stored_key = parts[2]
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
            return hmac.compare_digest(key.hex(), stored_key)
        except Exception:
            return False
    if _password_hash is not None:
        try:
            return _password_hash.verify(password, password_hash)
        except Exception:
            pass
    return False
