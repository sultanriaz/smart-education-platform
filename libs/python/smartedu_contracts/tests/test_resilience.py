from __future__ import annotations

import httpx
import pytest

from smartedu_contracts.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    ResilientHttpClient,
    RetryPolicy,
)


def test_retries_retryable_get_and_then_succeeds():
    calls = {"value": 0}

    def handler(request: httpx.Request):
        calls["value"] += 1
        if calls["value"] < 3:
            return httpx.Response(503, request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    client = ResilientHttpClient(
        base_url="http://service.test",
        service_name="caller",
        retry_policy=RetryPolicy(
            max_attempts=3,
            backoff_seconds=0,
            max_backoff_seconds=0,
        ),
        transport=httpx.MockTransport(handler),
        sleeper=lambda _delay: None,
    )
    response = client.request("GET", "/health")
    client.close()

    assert response.status_code == 200
    assert calls["value"] == 3


def test_post_is_not_retried_without_idempotency_key():
    calls = {"value": 0}

    def handler(request: httpx.Request):
        calls["value"] += 1
        return httpx.Response(503, request=request)

    client = ResilientHttpClient(
        base_url="http://service.test",
        service_name="caller",
        retry_policy=RetryPolicy(
            max_attempts=3,
            backoff_seconds=0,
            max_backoff_seconds=0,
        ),
        transport=httpx.MockTransport(handler),
        sleeper=lambda _delay: None,
    )
    response = client.request("POST", "/create")
    client.close()

    assert response.status_code == 503
    assert calls["value"] == 1


def test_post_can_retry_with_idempotency_key():
    calls = {"value": 0}

    def handler(request: httpx.Request):
        calls["value"] += 1
        return httpx.Response(
            503 if calls["value"] == 1 else 201,
            request=request,
        )

    client = ResilientHttpClient(
        base_url="http://service.test",
        service_name="caller",
        retry_policy=RetryPolicy(
            max_attempts=2,
            backoff_seconds=0,
            max_backoff_seconds=0,
        ),
        transport=httpx.MockTransport(handler),
        sleeper=lambda _delay: None,
    )
    response = client.request(
        "POST",
        "/create",
        idempotency_key="create-1",
    )
    client.close()

    assert response.status_code == 201
    assert calls["value"] == 2


def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreaker(
        CircuitBreakerConfig(
            failure_threshold=2,
            recovery_seconds=60,
        )
    )
    breaker.failure()
    breaker.failure()

    with pytest.raises(CircuitOpenError):
        breaker.before_call()
