from __future__ import annotations

import os

import httpx
import pytest

BASE = os.getenv("SMARTEDU_GATEWAY_URL", "").rstrip("/")


@pytest.mark.live
@pytest.mark.skipif(not BASE, reason="SMARTEDU_GATEWAY_URL not configured")
def test_unknown_route_uses_standard_error_shape():
    response = httpx.get(BASE + "/api/v1/not-a-service/test", timeout=5.0)
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "route_not_found"
    assert body["error"]["request_id"]
    assert body["error"]["correlation_id"]


@pytest.mark.live
@pytest.mark.skipif(not BASE, reason="SMARTEDU_GATEWAY_URL not configured")
def test_malicious_correlation_id_is_not_reflected():
    value = 'bad"\nheader'
    response = httpx.get(
        BASE + "/health",
        headers={"X-Correlation-ID": value},
        timeout=5.0,
    )
    assert response.status_code == 200
    assert response.headers.get("x-correlation-id") != value
