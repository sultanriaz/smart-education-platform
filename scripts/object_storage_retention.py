from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import boto3
from botocore.client import Config

from smartedu_infra.settings import ObjectStorageSettings

DEFAULT_POLICIES = {
    "platform-imports": 7,
    "platform-exports": 30,
    "report-exports": 14,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    settings = ObjectStorageSettings()
    client = boto3.client(
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

    now = datetime.now(timezone.utc)
    deleted = 0

    for bucket, days in DEFAULT_POLICIES.items():
        cutoff = now - timedelta(days=days)
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket):
            for item in page.get("Contents", []):
                if item["LastModified"] >= cutoff:
                    continue
                print(
                    f"{'DELETE' if args.apply else 'WOULD DELETE'} "
                    f"s3://{bucket}/{item['Key']}"
                )
                if args.apply:
                    client.delete_object(Bucket=bucket, Key=item["Key"])
                    deleted += 1

    print(f"Deleted {deleted} objects." if args.apply else "Dry run complete.")


if __name__ == "__main__":
    main()
