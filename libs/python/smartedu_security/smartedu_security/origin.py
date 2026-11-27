from __future__ import annotations

from urllib.parse import urlparse

from fastapi import HTTPException, Request


def normalize_origin(origin: str) -> str:
    parsed = urlparse(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid origin")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _request_origin(request: Request) -> str | None:
    host = (
        request.headers.get("x-forwarded-host")
        or request.headers.get("host")
        or ""
    ).split(",")[0].strip()
    if not host or host in {"testserver", "testserver.local"}:
        return None
    scheme = (
        request.headers.get("x-forwarded-proto")
        or request.url.scheme
        or "https"
    ).split(",")[0].strip().lower()
    if scheme not in {"http", "https"}:
        return None
    try:
        return normalize_origin(f"{scheme}://{host}")
    except ValueError:
        return None


def require_trusted_origin(
    request: Request,
    trusted_origins: tuple[str, ...],
    *,
    allow_missing: bool = False,
) -> None:
    origin = request.headers.get("origin") or request.headers.get("referer")
    if not origin:
        if allow_missing:
            return
        raise HTTPException(status_code=403, detail="Missing request origin")

    try:
        normalized = normalize_origin(origin)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Untrusted request origin") from exc

    allowed: set[str] = set()
    for value in trusted_origins:
        candidate = value.strip()
        if not candidate or candidate == "*":
            continue
        try:
            allowed.add(normalize_origin(candidate))
        except ValueError:
            continue

    same_origin = _request_origin(request)
    if normalized in allowed or (same_origin is not None and normalized == same_origin):
        return

    raise HTTPException(status_code=403, detail="Untrusted request origin")
