from __future__ import annotations

import httpx


class SequenceTransport(httpx.AsyncBaseTransport):
    """Deterministic HTTP transport for retry/circuit-breaker tests."""

    def __init__(self, statuses: list[int], *, payload: dict | None = None):
        if not statuses:
            raise ValueError("statuses cannot be empty")
        self.statuses = list(statuses)
        self.payload = payload or {"ok": True}
        self.calls = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        index = min(self.calls, len(self.statuses) - 1)
        status = self.statuses[index]
        self.calls += 1
        return httpx.Response(
            status,
            json=self.payload,
            request=request,
        )
