import hashlib
import hmac

try:
    from pwdlib import PasswordHash

    _password_hash = PasswordHash.recommended()
except Exception:
    _password_hash = None


def hash_password(password: str) -> str:
    if _password_hash is None:
        raise RuntimeError("Argon2 password hasher (pwdlib[argon2]) is unavailable.")
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("pbkdf2:sha256:"):
        try:
            parts = password_hash.split("$")
            iterations = int(parts[0].split(":")[2])
            salt = parts[1]
            stored_key = parts[2]
            key = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
            )
            return hmac.compare_digest(key.hex(), stored_key)
        except Exception:
            return False
    if _password_hash is not None:
        try:
            return _password_hash.verify(password, password_hash)
        except Exception:
            pass
    return False
