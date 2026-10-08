"""Generate local signing keys once; never overwrite an existing key pair."""

import argparse
import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(".secrets"))
    args = parser.parse_args()
    private_path = args.directory / "identity-private.pem"
    public_path = args.directory / "identity-public.pem"
    if private_path.exists() or public_path.exists():
        parser.error("A key file already exists. Choose a new directory for rotation.")
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    args.directory.mkdir(parents=True, exist_ok=True)
    private_bytes = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    descriptor = os.open(private_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as private_file:
        private_file.write(private_bytes)
    with public_path.open("xb") as public_file:
        public_file.write(
            key.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
    print(f"Created key pair in {args.directory}. Keep the private key out of images and Git.")


if __name__ == "__main__":
    main()
