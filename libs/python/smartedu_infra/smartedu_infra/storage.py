from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import BinaryIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .settings import ObjectStorageSettings


@dataclass(frozen=True, slots=True)
class StoredObject:
    bucket: str
    key: str
    etag: str | None
    size: int | None = None


class ObjectStorage:
    def __init__(self, client, *, presign_ttl_seconds: int):
        self.client = client
        self.presign_ttl_seconds = presign_ttl_seconds

    @classmethod
    def from_settings(cls, settings: ObjectStorageSettings) -> ObjectStorage:
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
        return cls(client, presign_ttl_seconds=settings.s3_presign_ttl_seconds)

    @staticmethod
    def safe_key(*parts: str) -> str:
        clean: list[str] = []
        for part in parts:
            value = part.strip().replace("\\", "/")
            path = PurePosixPath(value)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Object key contains unsafe path traversal")
            clean.extend(p for p in path.parts if p not in {"", "."})
        if not clean:
            raise ValueError("Object key cannot be empty")
        return "/".join(clean)

    def ensure_bucket(self, bucket: str) -> None:
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)

    def upload_fileobj(
        self,
        *,
        bucket: str,
        key: str,
        fileobj: BinaryIO,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> StoredObject:
        safe_key = self.safe_key(key)
        extra: dict[str, object] = {}
        if content_type:
            extra["ContentType"] = content_type
        if metadata:
            extra["Metadata"] = metadata

        self.client.upload_fileobj(
            fileobj,
            bucket,
            safe_key,
            ExtraArgs=extra or None,
        )
        head = self.client.head_object(Bucket=bucket, Key=safe_key)
        return StoredObject(
            bucket=bucket,
            key=safe_key,
            etag=str(head.get("ETag", "")).strip('"') or None,
            size=head.get("ContentLength"),
        )

    def presign_get(self, *, bucket: str, key: str) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": self.safe_key(key)},
            ExpiresIn=self.presign_ttl_seconds,
        )

    def presign_put(
        self,
        *,
        bucket: str,
        key: str,
        content_type: str | None = None,
    ) -> str:
        params: dict[str, object] = {
            "Bucket": bucket,
            "Key": self.safe_key(key),
        }
        if content_type:
            params["ContentType"] = content_type
        return self.client.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=self.presign_ttl_seconds,
        )

    def delete(self, *, bucket: str, key: str) -> None:
        self.client.delete_object(Bucket=bucket, Key=self.safe_key(key))
