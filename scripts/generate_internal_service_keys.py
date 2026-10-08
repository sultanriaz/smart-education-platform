from __future__ import annotations

import argparse
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SERVICES = [
    "identity-service",
    "academic-service",
    "attendance-service",
    "scheduling-service",
    "notification-service",
    "facility-service",
    "learning-service",
    "assessment-service",
    "reporting-service",
    "platform-service",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="secrets-local/internal-service-keys",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    for service in SERVICES:
        private = Ed25519PrivateKey.generate()
        private_bytes = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = private.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        private_path = output / f"{service}.private.pem"
        public_path = output / f"{service}.public.pem"
        private_path.write_bytes(private_bytes)
        public_path.write_bytes(public_bytes)

        try:
            private_path.chmod(0o600)
        except OSError:
            pass

    print(f"Generated {len(SERVICES)} Ed25519 service key pairs in {output}")
    print("Keep *.private.pem out of Git and container images.")


if __name__ == "__main__":
    main()
