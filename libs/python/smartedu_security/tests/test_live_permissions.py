"""Custom cross-service grants must be checked live, not cached from a JWT."""
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException

from smartedu_security.live_permissions import live_permission


@pytest.fixture
def principal():
    return SimpleNamespace(user_id=uuid4(), permissions=frozenset({"academic.records.read"}),
                           raw_token="signed-test-fixture")


def test_ungranted_scope_never_calls_identity(monkeypatch, principal):
    monkeypatch.setattr(httpx, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    assert live_permission(principal, "academic.records.write", "http://localhost:8001/.well-known/jwks.json") is False


@pytest.mark.parametrize("status,expect", [(200, True), (401, 403), (403, 403), (500, 503)])
def test_status_handling(monkeypatch, principal, status, expect):
    def respond(url, **kw):
        assert url == "http://localhost:8001/api/v1/auth/access-status"
        assert kw["headers"]["Authorization"] == "Bearer signed-test-fixture"
        return httpx.Response(status, json={"user_id": str(principal.user_id), "active": True})
    monkeypatch.setattr(httpx, "get", respond)
    if expect is True:
        assert live_permission(principal, "academic.records.read", "http://localhost:8001/.well-known/jwks.json")
    else:
        with pytest.raises(HTTPException) as error:
            live_permission(principal, "academic.records.read", "http://localhost:8001/.well-known/jwks.json")
        assert error.value.status_code == expect


@pytest.mark.parametrize("body", [{"active": False}, {"active": True, "user_id": str(uuid4())},
                                   {"active": "true"}, {}, [], "not json"])
def test_identity_mismatch_and_corrupt_json_fail_closed(monkeypatch, principal, body):
    monkeypatch.setattr(httpx, "get", lambda *a, **kw: httpx.Response(200, json=body))
    with pytest.raises(HTTPException) as error:
        live_permission(principal, "academic.records.read", "http://localhost:8001/.well-known/jwks.json")
    assert error.value.status_code in (403, 503)


def test_network_outage_fails_closed(monkeypatch, principal):
    monkeypatch.setattr(httpx, "get", lambda *a, **kw: (_ for _ in ()).throw(httpx.ConnectError("offline")))
    with pytest.raises(HTTPException) as error:
        live_permission(principal, "academic.records.read", "http://localhost:8001/.well-known/jwks.json")
    assert error.value.status_code == 503


def test_missing_token_cannot_activate_scope(principal):
    principal.raw_token = ""
    with pytest.raises(HTTPException) as error:
        live_permission(principal, "academic.records.read", "http://localhost:8001/.well-known/jwks.json")
    assert error.value.status_code == 403
