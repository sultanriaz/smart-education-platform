from __future__ import annotations

import hashlib
import io
import logging
import os
import re

logger = logging.getLogger("learning-service.parser")

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pptx
except ImportError:
    pptx = None

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".md": "text/plain",
}


class DocumentParsingError(Exception):
    """Raised when parsing or extracting text from a document fails."""
    pass


def compute_sha256(data: bytes) -> str:
    """Computes the SHA-256 hash of raw file bytes for deduplication."""
    return hashlib.sha256(data).hexdigest()


def detect_file_type(filename: str, mime_type: str | None = None) -> tuple[str, str]:
    """Validates extension and returns (file_type, canonical_mime).

    e.g. ('pdf', 'application/pdf')
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentParsingError(
            f"Unsupported file format '{ext}'. Allowed formats: .pdf, .docx, .pptx, .txt"
        )
    canonical_mime = ALLOWED_EXTENSIONS[ext]
    file_type = ext.lstrip(".")
    return file_type, canonical_mime


def extract_text(file_type: str, data: bytes) -> str:
    """Extracts plain text from the given document bytes."""
    if not data:
        raise DocumentParsingError("File is empty (0 bytes).")

    file_type = file_type.lower()
    if file_type == "pdf":
        return _extract_pdf(data)
    elif file_type == "docx":
        return _extract_docx(data)
    elif file_type == "pptx":
        return _extract_pptx(data)
    elif file_type in ("txt", "md"):
        return _extract_txt(data)
    else:
        raise DocumentParsingError(f"Unsupported document type: {file_type}")


def _extract_pdf(data: bytes) -> str:
    # First attempt with pypdf
    text_parts: list[str] = []
    if pypdf is not None:
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{page_text.strip()}")
        except Exception as e:
            logger.warning("pypdf extraction failed, trying pdfplumber: %s", e)

    # Fallback to pdfplumber if pypdf got nothing or failed
    if not text_parts and pdfplumber is not None:
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    pt = page.extract_text()
                    if pt and pt.strip():
                        text_parts.append(f"--- Page {page_num + 1} ---\n{pt.strip()}")
        except Exception as e:
            logger.warning("pdfplumber extraction failed: %s", e)

    full_text = "\n\n".join(text_parts).strip()
    if not full_text:
        # Some PDFs may be scanned or image-based
        full_text = "PDF Document: Text content could not be extracted (may contain scanned images)."
    return full_text


def _extract_docx(data: bytes) -> str:
    if docx is None:
        raise DocumentParsingError("python-docx library is not installed.")
    try:
        doc = docx.Document(io.BytesIO(data))
        parts = []
        for p in doc.paragraphs:
            if p.text and p.text.strip():
                parts.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    parts.append(row_text)
        return "\n\n".join(parts).strip()
    except Exception as e:
        raise DocumentParsingError(f"Failed to parse DOCX document: {e}") from e


def _extract_pptx(data: bytes) -> str:
    if pptx is None:
        raise DocumentParsingError("python-pptx library is not installed.")
    try:
        prs = pptx.Presentation(io.BytesIO(data))
        parts = []
        for slide_num, slide in enumerate(prs.slides):
            slide_texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        if paragraph.text and paragraph.text.strip():
                            slide_texts.append(paragraph.text.strip())
            if slide_texts:
                parts.append(f"--- Slide {slide_num + 1} ---\n" + "\n".join(slide_texts))
        return "\n\n".join(parts).strip()
    except Exception as e:
        raise DocumentParsingError(f"Failed to parse PPTX presentation: {e}") from e


def _extract_txt(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"):
        try:
            return data.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace").strip()


def chunk_text(
    text: str,
    chunk_size_chars: int = 2000,
    chunk_overlap_chars: int = 200,
) -> list[str]:
    """Semantic sliding-window text chunker respecting paragraph and sentence boundaries."""
    if not text or not text.strip():
        return []

    text = text.strip()
    if len(text) <= chunk_size_chars:
        return [text]

    # Split by double newline first (paragraphs)
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= chunk_size_chars:
            current_chunk = f"{current_chunk}\n\n{para}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
                # Overlap: keep tail of previous chunk
                overlap_text = current_chunk[-chunk_overlap_chars:] if len(current_chunk) > chunk_overlap_chars else ""
                current_chunk = f"{overlap_text}\n\n{para}".strip() if overlap_text else para
            else:
                # The paragraph itself exceeds chunk_size_chars, split by sentence or slice
                for i in range(0, len(para), chunk_size_chars - chunk_overlap_chars):
                    sub = para[i : i + chunk_size_chars]
                    chunks.append(sub)
                current_chunk = ""

    if current_chunk and current_chunk not in chunks:
        chunks.append(current_chunk)

    return chunks
