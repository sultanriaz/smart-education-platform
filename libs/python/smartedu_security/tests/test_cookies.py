from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from smartedu_security import SecuritySettings, set_refresh_cookie


def test_refresh_cookie_is_httponly_and_samesite_strict():
    app = FastAPI()

    @app.post("/login")
    def login(response: Response):
        settings = SecuritySettings(
            REFRESH_COOKIE_SECURE=True,
            REFRESH_COOKIE_SAMESITE="strict",
        )
        set_refresh_cookie(response, "refresh-token", settings)
        return {"access_token": "access"}

    response = TestClient(app).post("/login")
    cookie = response.headers["set-cookie"]

    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=strict" in cookie
    assert "Path=/api/v1/identity/auth" in cookie
