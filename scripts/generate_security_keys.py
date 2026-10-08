from __future__ import annotations

import secrets

from smartedu_security import generate_encryption_key


def main() -> None:
    print("SECURITY_TOKEN_PEPPER=" + secrets.token_urlsafe(48))
    print(
        "SECURITY_NOTIFICATION_ENCRYPTION_KEY="
        + generate_encryption_key()
    )


if __name__ == "__main__":
    main()
