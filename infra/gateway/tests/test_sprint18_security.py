from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "templates" / "default.conf.template").read_text(encoding="utf-8")
SNIPPET = (ROOT / "snippets" / "proxy_common.conf").read_text(encoding="utf-8")


def test_high_risk_identity_rate_limit_zones_exist():
    assert "zone=login_api" in TEMPLATE
    assert "zone=refresh_api" in TEMPLATE
    assert "zone=recovery_api" in TEMPLATE


def test_login_has_exact_stricter_location():
    assert "location = /api/v1/identity/auth/login" in TEMPLATE
    assert "limit_req zone=login_api" in TEMPLATE


def test_recovery_routes_have_strict_edge_throttle():
    for route in [
        "/api/v1/identity/auth/password/forgot",
        "/api/v1/identity/auth/password/reset",
        "/api/v1/identity/auth/email/verification/request",
        "/api/v1/identity/auth/email/verification/confirm",
    ]:
        assert f"location = {route}" in TEMPLATE


def test_sensitive_auth_responses_are_no_store():
    assert 'Cache-Control "no-store, max-age=0"' in TEMPLATE


def test_credentials_cors_and_requested_with_are_supported():
    assert 'Access-Control-Allow-Credentials "true"' in SNIPPET
    assert "X-Requested-With" in SNIPPET


def test_gateway_security_headers_are_present():
    for header in [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
        "X-Permitted-Cross-Domain-Policies",
        "X-DNS-Prefetch-Control",
    ]:
        assert header in TEMPLATE
