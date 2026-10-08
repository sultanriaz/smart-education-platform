from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StoredObject:
    key: str
    size_bytes: int
    checksum_sha256: str
    mime_type: str


class StorageBackend(Protocol):
    def put_bytes(self, key: str, data: bytes, mime_type: str) -> StoredObject: ...
    def get_bytes(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
