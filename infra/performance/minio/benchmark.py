from __future__ import annotations

import argparse
import io
import os
import statistics
import time
import uuid

import boto3
from botocore.client import Config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default=os.getenv("S3_ENDPOINT_URL", "http://localhost:59000"))
    parser.add_argument("--bucket", default=os.getenv("PERF_S3_BUCKET", "platform-imports"))
    parser.add_argument("--objects", type=int, default=50)
    parser.add_argument("--size-kb", type=int, default=256)
    args = parser.parse_args()

    client = boto3.client(
        "s3",
        endpoint_url=args.endpoint,
        region_name=os.getenv("S3_REGION", "us-east-1"),
        aws_access_key_id=os.environ["S3_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_SECRET_ACCESS_KEY"],
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )

    data = b"x" * (args.size_kb * 1024)
    upload_ms: list[float] = []
    download_ms: list[float] = []
    keys: list[str] = []

    try:
        for _ in range(args.objects):
            key = f"perf/{uuid.uuid4()}.bin"
            keys.append(key)
            start = time.perf_counter()
            client.upload_fileobj(io.BytesIO(data), args.bucket, key)
            upload_ms.append((time.perf_counter() - start) * 1000)

        for key in keys:
            target = io.BytesIO()
            start = time.perf_counter()
            client.download_fileobj(args.bucket, key, target)
            download_ms.append((time.perf_counter() - start) * 1000)
            if len(target.getvalue()) != len(data):
                raise RuntimeError("downloaded object length mismatch")
    finally:
        for key in keys:
            try:
                client.delete_object(Bucket=args.bucket, Key=key)
            except Exception:
                pass

    def p95(values):
        ordered = sorted(values)
        return ordered[max(0, int(len(ordered) * 0.95) - 1)]

    print(f"objects={args.objects}")
    print(f"size_kb={args.size_kb}")
    print(f"upload_avg_ms={statistics.mean(upload_ms):.2f}")
    print(f"upload_p95_ms={p95(upload_ms):.2f}")
    print(f"download_avg_ms={statistics.mean(download_ms):.2f}")
    print(f"download_p95_ms={p95(download_ms):.2f}")


if __name__ == "__main__":
    main()
