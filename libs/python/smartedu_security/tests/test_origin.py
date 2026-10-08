from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from smartedu_security import require_trusted_origin


def make_app():
    app = FastAPI()

    @app.post("/cookie-action")
    def cookie_action(request: Request):
        require_trusted_origin(
            request,
            ("https://app.example.edu",),
        )
        return {"ok": True}

    return app


def test_trusted_origin_passes():
    response = TestClient(make_app()).post(
        "/cookie-action",
        headers={"Origin": "https://app.example.edu"},
    )
    assert response.status_code == 200


def test_missing_origin_is_rejected_for_cookie_action():
    response = TestClient(make_app()).post("/cookie-action")
    assert response.status_code == 403


def test_untrusted_origin_is_rejected():
    response = TestClient(make_app()).post(
        "/cookie-action",
        headers={"Origin": "https://evil.example"},
    )
    assert response.status_code == 403
