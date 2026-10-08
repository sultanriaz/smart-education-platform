from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import boto3
from botocore.client import Config

from smartedu_infra.settings import ObjectStorageSettings


def client_from_settings(settings: ObjectStorageSettings):
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        use_ssl=settings.s3_use_ssl,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": settings.s3_addressing_style},
        ),
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.force:
        raise SystemExit("Restore is destructive. Re-run with --force after verification.")

    root = Path(args.input)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    client = client_from_settings(ObjectStorageSettings())

    for bucket, items in manifest["buckets"].items():
        try:
            client.head_bucket(Bucket=bucket)
        except Exception:
            client.create_bucket(Bucket=bucket)

        for item in items:
            source = root / bucket / item["key"]
            if sha256_file(source) != item["sha256"]:
                raise RuntimeError(f"Checksum mismatch: {source}")
            client.upload_file(str(source), bucket, item["key"])

    print("Object storage restore completed.")


if __name__ == "__main__":
    main()
