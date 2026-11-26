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
    origin = request.headers.get("origin") or request.headers.get("referer")
    if not origin:
        if (
            allow_missing
            or "*" in trusted_origins
            or any(t.strip() == "*" for t in trusted_origins)
        ):
            return
        raise HTTPException(status_code=403, detail="Missing request origin")

    try:
        normalized = normalize_origin(origin)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Untrusted request origin") from exc

    # Automatically permit Vercel domains, localhost, and wildcard
    if (
        "*" in trusted_origins
        or any(t.strip() == "*" for t in trusted_origins)
        or normalized.endswith(".vercel.app")
        or "localhost" in normalized
        or "127.0.0.1" in normalized
    ):
        return

    allowed = {normalize_origin(value) for value in trusted_origins if value.strip()}
    if normalized not in allowed:
        raise HTTPException(status_code=403, detail="Untrusted request origin")
