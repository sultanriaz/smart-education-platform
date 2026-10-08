from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "templates" / "default.conf.template").read_text(encoding="utf-8")
NGINX = (ROOT / "nginx.conf").read_text(encoding="utf-8")
SNIPPET = (ROOT / "snippets" / "proxy_common.conf").read_text(encoding="utf-8")


def test_gateway_propagates_workflow_context():
    assert "X-Request-ID $request_id" in SNIPPET
    assert "X-Correlation-ID $correlation_id" in SNIPPET
    assert "X-Causation-ID $http_x_causation_id" in SNIPPET
    assert "traceparent $http_traceparent" in SNIPPET


def test_gateway_propagates_idempotency_key():
    assert "Idempotency-Key $http_idempotency_key" in SNIPPET
    assert "Idempotency-Key" in SNIPPET


def test_cors_allows_sprint16_headers():
    for header in [
        "X-Correlation-ID",
        "X-Causation-ID",
        "Idempotency-Key",
        "traceparent",
    ]:
        assert header in SNIPPET


def test_gateway_exposes_correlation_response_header():
    assert "X-Correlation-ID $correlation_id" in TEMPLATE
    assert "X-Correlation-ID" in TEMPLATE


def test_gateway_logs_correlation_without_logging_idempotency_value():
    assert '"correlation_id":"$correlation_id"' in NGINX
    assert '"idempotency_key_present":$has_idempotency_key' in NGINX
    assert '"idempotency_key":"$http_idempotency_key"' not in NGINX


def test_gateway_errors_include_correlation_id():
    assert '"correlation_id":"$correlation_id"' in TEMPLATE
