from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from app.storage.dependencies import get_storage_backend
from app.storage.local import LocalStorageBackend


def test_local_storage_round_trip(storage):
    stored = storage.put_bytes("a/b.txt", b"hello", "text/plain")
    assert stored.size_bytes == 5
    assert stored.checksum_sha256 == hashlib.sha256(b"hello").hexdigest()
    assert storage.get_bytes("a/b.txt") == b"hello"
    storage.delete("a/b.txt")


def test_local_storage_falls_back_to_tmp_on_read_only_fs(monkeypatch, tmp_path):
    readonly_path = tmp_path / "readonly" / "objects"
    fallback_dir = tmp_path / "tmp_fallback"
    original_mkdir = Path.mkdir

    def fake_mkdir(self, *args, **kwargs):
        if self == readonly_path.resolve():
            raise OSError(30, "Read-only file system")
        return original_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(fallback_dir))

    backend = LocalStorageBackend(readonly_path)
    assert backend.base_path == (fallback_dir / "smartedu-learning-objects").resolve()
    stored = backend.put_bytes("sub/doc.txt", b"ok", "text/plain")
    assert stored.size_bytes == 2
    assert backend.get_bytes("sub/doc.txt") == b"ok"


def test_get_storage_backend_allows_vercel_local_fallback(monkeypatch, tmp_path):
    from app.core.config import settings

    get_storage_backend.cache_clear()
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", tmp_path / "objects")
    try:
        backend = get_storage_backend()
        assert isinstance(backend, LocalStorageBackend)
    finally:
        get_storage_backend.cache_clear()
