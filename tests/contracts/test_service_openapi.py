from __future__ import annotations

import os

import httpx
import pytest

SERVICES = {
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
@pytest.mark.parametrize("service", sorted(SERVICES))
def test_service_health_and_openapi(service):
    base = (SERVICES[service] or "").rstrip("/")
    if not base:
        pytest.skip(f"{service} URL not configured")

    health = httpx.get(base + "/health", timeout=5.0)
    assert health.status_code == 200

    openapi = httpx.get(base + "/openapi.json", timeout=5.0)
    assert openapi.status_code == 200
    document = openapi.json()
    assert isinstance(document.get("paths"), dict)
    assert "/health" in document["paths"]
    assert "/ready" in document["paths"]
