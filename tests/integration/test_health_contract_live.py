from __future__ import annotations

import os
import time

import httpx
import pytest

SERVICE_URLS = {
    "identity": os.getenv("IDENTITY_SERVICE_URL"),
    "academic": os.getenv("ACADEMIC_SERVICE_URL"),
    "attendance": os.getenv("ATTENDANCE_SERVICE_URL"),
    "scheduling": os.getenv("SCHEDULING_SERVICE_URL"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL"),
    "facility": os.getenv("FACILITY_SERVICE_URL"),
    "learning": os.getenv("LEARNING_SERVICE_URL"),
    "assessment": os.getenv("ASSESSMENT_SERVICE_URL"),
    "reporting": os.getenv("REPORTING_SERVICE_URL"),
    "platform": os.getenv("PLATFORM_SERVICE_URL"),
}


@pytest.mark.live
@pytest.mark.parametrize("service", sorted(SERVICE_URLS))
def test_health_is_fast_and_readiness_is_explicit(service):
    base = (SERVICE_URLS[service] or "").rstrip("/")
    if not base:
        pytest.skip(f"{service} URL is not configured")

    started = time.perf_counter()
    health = httpx.get(base + "/health", timeout=3.0)
    elapsed = time.perf_counter() - started

    assert health.status_code == 200
    assert elapsed < 1.0, f"{service} /health took {elapsed:.3f}s"

    ready = httpx.get(base + "/ready", timeout=5.0)
    assert ready.status_code in {200, 503}
    assert "application/json" in ready.headers.get("content-type", "")
