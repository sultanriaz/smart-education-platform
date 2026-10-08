from __future__ import annotations

from urllib.parse import urlparse

from fastapi import HTTPException, Request


def normalize_origin(origin: str) -> str:
    parsed = urlparse(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid origin")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def require_trusted_origin(
    request: Request,
    trusted_origins: tuple[str, ...],
    *,
    allow_missing: bool = False,
) -> None:
    origin = request.headers.get("origin")
    if not origin:
        if allow_missing:
            return
        raise HTTPException(status_code=403, detail="Missing request origin")

    try:
        normalized = normalize_origin(origin)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Untrusted request origin") from exc

    allowed = {normalize_origin(value) for value in trusted_origins}
    if normalized not in allowed:
        raise HTTPException(status_code=403, detail="Untrusted request origin")
