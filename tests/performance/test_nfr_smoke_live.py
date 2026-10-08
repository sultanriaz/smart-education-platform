from __future__ import annotations

import os
import statistics
import time

import httpx
import pytest

GATEWAY = os.getenv("SMARTEDU_GATEWAY_URL", "").rstrip("/")


@pytest.mark.live
@pytest.mark.skipif(not GATEWAY, reason="SMARTEDU_GATEWAY_URL not configured")
def test_gateway_health_smoke_latency():
    durations = []
    with httpx.Client(timeout=3.0) as client:
        for _ in range(10):
            start = time.perf_counter()
            response = client.get(GATEWAY + "/health")
            durations.append(time.perf_counter() - start)
            assert response.status_code == 200

    p95 = sorted(durations)[int(len(durations) * 0.95) - 1]
    assert p95 < 1.0, (
        f"Gateway /health p95 was {p95:.3f}s; this is a smoke gate, "
        "not the Sprint 20 load test."
    )
    print(
        f"health mean={statistics.mean(durations):.3f}s "
        f"p95={p95:.3f}s"
    )
