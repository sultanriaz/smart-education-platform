from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.client import Config

from smartedu_infra.naming import DEFAULT_BUCKETS
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


def backup_bucket(client, bucket: str, output_root: Path) -> list[dict]:
    bucket_root = output_root / bucket
    bucket_root.mkdir(parents=True, exist_ok=True)
    manifest = []

    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for item in page.get("Contents", []):
            key = item["Key"]
            target = bucket_root / Path(key)
            target.parent.mkdir(parents=True, exist_ok=True)
            client.download_file(bucket, key, str(target))
            manifest.append(
                {
                    "key": key,
                    "size": target.stat().st_size,
                    "sha256": sha256_file(target),
                    "last_modified": item["LastModified"].astimezone(timezone.utc).isoformat(),
                }
            )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--buckets",
        nargs="*",
        default=list(DEFAULT_BUCKETS),
    )
    args = parser.parse_args()

    settings = ObjectStorageSettings()
    client = client_from_settings(settings)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "buckets": {},
    }
    for bucket in args.buckets:
        print(f"Backing up s3://{bucket}")
        manifest["buckets"][bucket] = backup_bucket(client, bucket, output)

    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    print(f"Object storage backup written to {output}")


if __name__ == "__main__":
    main()
