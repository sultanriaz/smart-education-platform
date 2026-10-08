import pytest

from smartedu_security import (
    FilePolicy,
    FileValidationError,
    sanitize_filename,
    validate_magic_prefix,
    validate_upload_metadata,
)

POLICY = FilePolicy(
    max_bytes=1024 * 1024,
    allowed_extensions=frozenset({".pdf", ".png", ".jpg", ".jpeg"}),
    allowed_mime_types=frozenset({"application/pdf", "image/png", "image/jpeg"}),
)


def test_filename_is_sanitized_to_basename():
    assert sanitize_filename("../../Week 1 Notes.pdf") == "Week 1 Notes.pdf"


def test_executable_is_rejected():
    with pytest.raises(FileValidationError):
        validate_upload_metadata(
            filename="payload.exe",
            content_type="application/octet-stream",
            size_bytes=10,
            policy=POLICY,
        )


def test_size_is_enforced():
    with pytest.raises(FileValidationError):
        validate_upload_metadata(
            filename="notes.pdf",
            content_type="application/pdf",
            size_bytes=2 * 1024 * 1024,
            policy=POLICY,
        )


def test_pdf_magic_is_validated():
    validate_magic_prefix("application/pdf", b"%PDF-1.7\n")
    with pytest.raises(FileValidationError):
        validate_magic_prefix("application/pdf", b"MZ....")
