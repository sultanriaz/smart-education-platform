from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import PurePath

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._ -]+")

SIGNATURES: dict[str, tuple[bytes, ...]] = {
    "application/pdf": (b"%PDF-",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/gif": (b"GIF87a", b"GIF89a"),
    "application/zip": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
}

DANGEROUS_EXTENSIONS = frozenset(
    {
        ".exe",
        ".dll",
        ".com",
        ".bat",
        ".cmd",
        ".ps1",
        ".sh",
        ".msi",
        ".scr",
        ".js",
        ".jar",
        ".vbs",
        ".hta",
        ".reg",
    }
)


@dataclass(frozen=True, slots=True)
class FilePolicy:
    max_bytes: int
    allowed_extensions: frozenset[str]
    allowed_mime_types: frozenset[str]


class FileValidationError(ValueError):
    pass


def sanitize_filename(filename: str) -> str:
    base = PurePath(filename.replace("\\", "/")).name.strip()
    if not base or base in {".", ".."}:
        raise FileValidationError("Invalid filename")
    cleaned = _SAFE_NAME.sub("_", base).strip(" .")
    if not cleaned:
        raise FileValidationError("Invalid filename")
    return cleaned[:180]


def validate_upload_metadata(
    *,
    filename: str,
    content_type: str,
    size_bytes: int,
    policy: FilePolicy,
) -> str:
    safe_name = sanitize_filename(filename)
    extension = os.path.splitext(safe_name)[1].lower()

    if extension in DANGEROUS_EXTENSIONS:
        raise FileValidationError("Executable/script uploads are not allowed")
    if extension not in policy.allowed_extensions:
        raise FileValidationError("File extension is not allowed")
    if content_type.casefold() not in {value.casefold() for value in policy.allowed_mime_types}:
        raise FileValidationError("MIME type is not allowed")
    if size_bytes < 0 or size_bytes > policy.max_bytes:
        raise FileValidationError("File exceeds the allowed size")
    return safe_name


def validate_magic_prefix(content_type: str, prefix: bytes) -> None:
    expected = SIGNATURES.get(content_type.casefold())
    if not expected:
        return
    if not any(prefix.startswith(signature) for signature in expected):
        raise FileValidationError("File content does not match declared MIME type")
