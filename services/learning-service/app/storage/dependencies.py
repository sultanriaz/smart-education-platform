from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.storage.local import LocalStorageBackend
from app.storage.s3 import S3StorageBackend


@lru_cache
def get_storage_backend():
    backend = settings.STORAGE_BACKEND.lower()
    if backend == "s3":
        return S3StorageBackend()
    if settings.ENVIRONMENT.lower() in {"production", "prod", "staging"}:
        raise RuntimeError("Hosted Learning storage must use a durable S3-compatible backend")
    if backend != "local":
        raise RuntimeError("Unsupported learning storage backend")
    return LocalStorageBackend(settings.LOCAL_STORAGE_PATH)
