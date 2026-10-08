from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from smartedu_contracts import (
    CORRELATION_ID_HEADER,
    REQUEST_ID_HEADER,
    install_platform_contracts,
)
from smartedu_contracts.context import get_correlation_id, get_request_id
from smartedu_contracts.idempotency import MemoryIdempotencyStore


def make_app():
    app = FastAPI()
    install_platform_contracts(
        app,
        service_name="test-service",
        idempotency_store=MemoryIdempotencyStore(),
        idempotency_excluded_path_prefixes=("/auth/",),
    )
    counter = {"value": 0}

    @app.get("/context")
    def context():
        return {
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
        }

    @app.post("/mutate")
    def mutate():
        counter["value"] += 1
        return {"count": counter["value"]}

    @app.post("/auth/login")
    def login():
        counter["value"] += 1
        return {"access_token": f"token-{counter['value']}"}

    return app


def test_context_headers_are_propagated():
    client = TestClient(make_app())
    response = client.get(
        "/context",
        headers={
            REQUEST_ID_HEADER: "gateway-request-1",
            CORRELATION_ID_HEADER: "flow-1",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "request_id": "gateway-request-1",
        "correlation_id": "flow-1",
    }
    assert response.headers[REQUEST_ID_HEADER] == "gateway-request-1"
    assert response.headers[CORRELATION_ID_HEADER] == "flow-1"


def test_idempotency_replays_successful_mutation():
    client = TestClient(make_app())
    headers = {"Idempotency-Key": "test-create-1"}

    first = client.post("/mutate", headers=headers)
    second = client.post("/mutate", headers=headers)

    assert first.status_code == 200
    assert first.json() == {"count": 1}
    assert second.status_code == 200
    assert second.json() == {"count": 1}
    assert second.headers["x-idempotent-replay"] == "true"


def test_idempotency_rejects_same_key_for_different_request():
    client = TestClient(make_app())
    headers = {"Idempotency-Key": "test-conflict-1"}

    assert client.post("/mutate?a=1", headers=headers).status_code == 200
    conflict = client.post("/mutate?a=2", headers=headers)

    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"


def test_excluded_sensitive_path_is_not_idempotency_cached():
    client = TestClient(make_app())
    headers = {"Idempotency-Key": "login-1"}

    first = client.post("/auth/login", headers=headers)
    second = client.post("/auth/login", headers=headers)

    assert first.json()["access_token"] == "token-1"
    assert second.json()["access_token"] == "token-2"


def test_idempotency_does_not_share_a_response_between_credentials():
    client = TestClient(make_app())
    first = {"Idempotency-Key": "same-user-supplied-key", "Authorization": "Bearer user-one"}
    second = {"Idempotency-Key": "same-user-supplied-key", "Authorization": "Bearer user-two"}
    assert client.post("/mutate", headers=first).json() == {"count": 1}
    assert client.post("/mutate", headers=second).json() == {"count": 2}
    assert client.post("/mutate", headers=first).json() == {"count": 1}


def test_expired_bearer_cannot_retrieve_an_authorized_replay(monkeypatch):
    import base64
    import json

    import smartedu_contracts.idempotency as module

    encoded = base64.urlsafe_b64encode(json.dumps({"exp": 110}).encode()).decode().rstrip("=")
    headers = {"Idempotency-Key": "expires", "Authorization": f"Bearer header.{encoded}.signature"}
    client = TestClient(make_app())
    monkeypatch.setattr(module.time, "time", lambda: 100)
    assert client.post("/mutate", headers=headers).json() == {"count": 1}
    assert client.post("/mutate", headers=headers).json() == {"count": 1}
    monkeypatch.setattr(module.time, "time", lambda: 120)
    # Domain auth is reached again; this fixture intentionally has no auth and
    # increments to prove the cached response was not returned.
    assert client.post("/mutate", headers=headers).json() == {"count": 2}
