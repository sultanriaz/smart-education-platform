from __future__ import annotations

import os
from functools import lru_cache

from app.core.config import settings
from app.storage.local import LocalStorageBackend
from app.storage.s3 import S3StorageBackend


@lru_cache
def get_storage_backend():
    backend = settings.STORAGE_BACKEND.lower()
    if backend == "s3":
        return S3StorageBackend()
    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
    if settings.ENVIRONMENT.lower() in {"production", "prod", "staging"} and not is_serverless:
        raise RuntimeError("Hosted Learning storage must use a durable S3-compatible backend")
    if backend != "local":
        raise RuntimeError("Unsupported learning storage backend")
    return LocalStorageBackend(settings.LOCAL_STORAGE_PATH)
