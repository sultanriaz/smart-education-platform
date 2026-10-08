from __future__ import annotations

import hashlib

import boto3
from botocore.config import Config

from app.core.config import settings
from app.storage.base import StoredObject


class S3StorageBackend:
    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            use_ssl=settings.S3_USE_SSL,
            config=Config(
                connect_timeout=3, read_timeout=10, retries={"mode": "standard", "max_attempts": 2}
            ),
        )

    def put_bytes(self, key: str, data: bytes, mime_type: str) -> StoredObject:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=mime_type)
        return StoredObject(
            key=key,
            size_bytes=len(data),
            checksum_sha256=hashlib.sha256(data).hexdigest(),
            mime_type=mime_type,
        )

    def get_bytes(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        with response["Body"] as stream:
            return stream.read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
