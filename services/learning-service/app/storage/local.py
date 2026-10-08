from __future__ import annotations

import hashlib
from pathlib import Path

from app.storage.base import StoredObject


class LocalStorageBackend:
    def __init__(self, base_path: Path):
        self.base_path = base_path.resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

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
