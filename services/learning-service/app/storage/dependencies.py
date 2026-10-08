from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.storage.local import LocalStorageBackend
from app.storage.s3 import S3StorageBackend


@lru_cache
def get_storage_backend():
    if settings.STORAGE_BACKEND.lower() == "s3":
        return S3StorageBackend()
    return LocalStorageBackend(settings.LOCAL_STORAGE_PATH)
