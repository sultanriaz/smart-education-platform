from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class ApiResult:
    status_code: int
    json: Any
    headers: dict[str, str]


async def request_json(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: Any | None = None,
    headers: dict[str, str] | None = None,
) -> ApiResult:
    merged = dict(headers or {})
    if token:
        merged["Authorization"] = f"Bearer {token}"

    response = await client.request(
        method,
        path,
        headers=merged,
        json=json_body,
    )
    if response.status_code == 204:
        body: Any = None
    else:
        content_type = response.headers.get("content-type", "")
        body = response.json() if "application/json" in content_type else response.text

    return ApiResult(
        status_code=response.status_code,
        json=body,
        headers=dict(response.headers),
    )
