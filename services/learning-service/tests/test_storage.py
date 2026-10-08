from __future__ import annotations

import hashlib


def test_local_storage_round_trip(storage):
    stored = storage.put_bytes("a/b.txt", b"hello", "text/plain")
    assert stored.size_bytes == 5
    assert stored.checksum_sha256 == hashlib.sha256(b"hello").hexdigest()
    assert storage.get_bytes("a/b.txt") == b"hello"
    storage.delete("a/b.txt")
