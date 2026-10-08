"""Validate bytes before private object persistence; fail closed when scanning."""

import io
import zipfile
from pathlib import PurePosixPath

from smartedu_security.clamav import ClamAVScanner, MalwareScanError
from smartedu_security.files import (
    FilePolicy,
    FileValidationError,
    validate_magic_prefix,
    validate_upload_metadata,
)

from app.core.config import settings
from app.core.errors import DependencyUnavailableError, ValidationDomainError

TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def validate_file(filename, content_type, data):
    try:
        safe = validate_upload_metadata(
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            policy=FilePolicy(
                settings.MAX_UPLOAD_BYTES,
                frozenset(TYPES),
                frozenset(settings.ALLOWED_UPLOAD_MIME_TYPES),
            ),
        )
        extension = PurePosixPath(safe).suffix.lower()
        if TYPES[extension] != content_type or not data:
            raise FileValidationError(
                "File extension and content type must match; empty files are not allowed"
            )
        validate_magic_prefix(content_type, data[:16])
        if extension == ".txt":
            data.decode("utf-8")
            if b"\x00" in data:
                raise FileValidationError("Plain text cannot contain binary data")
        if extension in {".docx", ".pptx"}:
            validate_magic_prefix("application/zip", data[:16])
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                entries = archive.infolist()
                if (
                    len(entries) > 2000
                    or sum(entry.file_size for entry in entries) > 100 * 1024 * 1024
                ):
                    raise FileValidationError("Office archive exceeds safe expansion limits")
                for entry in entries:
                    path = PurePosixPath(entry.filename.replace("\\", "/"))
                    if (
                        path.is_absolute()
                        or ".." in path.parts
                        or ":" in entry.filename
                        or entry.flag_bits & 1
                    ):
                        raise FileValidationError("Unsafe Office archive path or encryption")
                    if entry.filename.lower().endswith("vbaproject.bin"):
                        raise FileValidationError("Office macros are not allowed")
                names = {entry.filename for entry in entries}
                folder = "word/" if extension == ".docx" else "ppt/"
                if "[Content_Types].xml" not in names or not any(
                    name.startswith(folder) for name in names
                ):
                    raise FileValidationError("File is not the declared Office document")
        if settings.MALWARE_SCAN_REQUIRED or settings.ENVIRONMENT.lower() in {"production", "prod"}:
            try:
                result = ClamAVScanner(
                    host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT
                ).scan_stream(io.BytesIO(data))
            except (OSError, MalwareScanError) as exc:
                raise DependencyUnavailableError("Required malware scanner is unavailable") from exc
            if not result.clean:
                raise FileValidationError("File was rejected by the malware scanner")
        return safe
    except (FileValidationError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
        raise ValidationDomainError(str(exc)) from exc
