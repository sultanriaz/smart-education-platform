from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "templates" / "default.conf.template").read_text(encoding="utf-8")
NGINX = (ROOT / "nginx.conf").read_text(encoding="utf-8")
SNIPPET = (ROOT / "snippets" / "proxy_common.conf").read_text(encoding="utf-8")

SERVICES = [
    "identity",
    "academic",
    "attendance",
    "scheduling",
    "notification",
    "facility",
    "learning",
    "assessment",
    "reporting",
    "platform",
]


def test_all_service_upstreams_declared():
    declarations = re.findall(r"^upstream\s+([a-z_]+)\s*\{", TEMPLATE, re.M)
    assert len(declarations) == 10
    for service in SERVICES:
        assert f"{service}_upstream" in declarations


def test_all_external_service_namespaces_exist():
    expected = {
        "identity": "/api/v1/identity/",
        "academic": "/api/v1/academic/",
        "attendance": "/api/v1/attendance/",
        "scheduling": "/api/v1/scheduling/",
        "notification": "/api/v1/notifications/",
        "facility": "/api/v1/facilities/",
        "learning": "/api/v1/learning/",
        "assessment": "/api/v1/assessments/",
        "reporting": "/api/v1/reporting/",
        "platform": "/api/v1/platform/",
    }
    for prefix in expected.values():
        assert prefix in TEMPLATE


def test_internal_routes_are_not_publicly_exposed():
    assert "location ^~ /api/v1/internal/" not in TEMPLATE
    namespaces = [
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
    ]
    for namespace in namespaces:
        assert f"/api/v1/{namespace}/internal/" in TEMPLATE


def test_request_id_generated_and_forwarded():
    assert "X-Request-ID $request_id" in TEMPLATE
    assert '"request_id":"$request_id"' in NGINX


def test_security_headers_exist():
    for header in [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    ]:
        assert header in TEMPLATE


def test_gateway_has_rate_limits():
    assert "limit_req_zone" in TEMPLATE
    assert "auth_api" in TEMPLATE
    assert "general_api" in TEMPLATE
    assert "limit_req_status 429" in TEMPLATE


def test_normalized_upstream_failure():
    assert "upstream_unavailable" in TEMPLATE
    assert '"code":"upstream_unavailable"' in TEMPLATE


def test_cors_is_exact_origin_based():
    assert "${CORS_ALLOWED_ORIGIN}" in TEMPLATE
    assert "Access-Control-Allow-Origin $cors_origin" in TEMPLATE
    assert "if ($request_method = OPTIONS)" in SNIPPET


def test_no_database_hostnames_in_gateway_config():
    combined = TEMPLATE + NGINX
    assert "postgres" not in combined.lower()
    assert "identity-db" not in combined
    assert "academic-db" not in combined
