from __future__ import annotations

import os

import httpx
import pytest

GATEWAY_URL = os.getenv("SMARTEDU_GATEWAY_URL", "").rstrip("/")


@pytest.mark.live
@pytest.mark.skipif(not GATEWAY_URL, reason="SMARTEDU_GATEWAY_URL is not configured")
@pytest.mark.parametrize(
    "namespace",
    [
        "identity",
        "academic",
        "attendance",
        "scheduling",
        "notifications",
        "facilities",
        "learning",
        "assessments",
        "reporting",
        "platform",
    ],
)
def test_internal_namespace_is_not_public(namespace):
    response = httpx.get(
        f"{GATEWAY_URL}/api/v1/{namespace}/internal/probe",
        timeout=5.0,
    )
    assert response.status_code == 404


@pytest.mark.live
@pytest.mark.skipif(not GATEWAY_URL, reason="SMARTEDU_GATEWAY_URL is not configured")
def test_gateway_correlation_headers():
    response = httpx.get(f"{GATEWAY_URL}/health", timeout=5.0)
    assert response.status_code == 200
    assert response.headers.get("x-request-id")
    assert response.headers.get("x-correlation-id")
