import io
import zipfile

import pytest

from app.core.config import settings
from app.core.errors import DependencyUnavailableError, ValidationDomainError
from app.security.uploads import validate_file


@pytest.mark.parametrize(
    "name,mime,data",
    [
        ("attack.exe", "application/pdf", b"%PDF-demo"),
        ("fake.pdf", "application/pdf", b"<script>alert(1)</script>"),
        ("fake.png", "image/png", b"%PDF-demo"),
        ("binary.txt", "text/plain", b"hello\x00world"),
        ("wrong.jpg", "application/pdf", b"%PDF-demo"),
    ],
)
def test_rejects_disguised_or_binary_uploads(name, mime, data):
    with pytest.raises(ValidationDomainError):
        validate_file(name, mime, data)


def test_safe_filename_and_pdf_signature():
    assert validate_file("../../lesson.pdf", "application/pdf", b"%PDF-demo") == "lesson.pdf"


def test_rejects_office_traversal():
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as archive:
        archive.writestr("[Content_Types].xml", "types")
        archive.writestr("word/document.xml", "document")
        archive.writestr("../evil", "payload")
    with pytest.raises(ValidationDomainError, match="Unsafe Office"):
        validate_file(
            "lesson.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            content.getvalue(),
        )


def test_required_scanner_outage_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "MALWARE_SCAN_REQUIRED", True)

    def unavailable(*_args):
        raise OSError("offline")

    monkeypatch.setattr("app.security.uploads.ClamAVScanner.scan_stream", unavailable)
    with pytest.raises(DependencyUnavailableError):
        validate_file("lesson.pdf", "application/pdf", b"%PDF-demo")
