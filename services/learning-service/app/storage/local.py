from __future__ import annotations

import hashlib
import logging
import tempfile
from pathlib import Path

from app.storage.base import StoredObject

logger = logging.getLogger("learning-service.storage.local")


class LocalStorageBackend:
    def __init__(self, base_path: Path):
        resolved = base_path.resolve()
        try:
            resolved.mkdir(parents=True, exist_ok=True)
            self.base_path = resolved
        except OSError as exc:
            # Serverless runtimes (e.g. Vercel /var/task) mount code read-only;
            # fall back to the writable temporary directory.
            fallback = (Path(tempfile.gettempdir()) / "smartedu-learning-objects").resolve()
            logger.warning(
                "Storage path %s is not writable (%s); falling back to %s",
                resolved,
                exc,
                fallback,
            )
            fallback.mkdir(parents=True, exist_ok=True)
            self.base_path = fallback

    def _path(self, key: str) -> Path:
        path = (self.base_path / key).resolve()
        if self.base_path not in path.parents and path != self.base_path:
            raise ValueError("Invalid storage key")
        return path

    def put_bytes(self, key: str, data: bytes, mime_type: str) -> StoredObject:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return StoredObject(
            key=key,
            size_bytes=len(data),
            checksum_sha256=hashlib.sha256(data).hexdigest(),
            mime_type=mime_type,
        )

    def get_bytes(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()
