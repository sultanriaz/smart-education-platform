from __future__ import annotations

import json
import os
import uuid
from typing import Any

from locust import HttpUser, between
from locust.exception import StopUser


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def json_env(name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = env(name)
    if not raw:
        return dict(default or {})
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"{name} must contain a JSON object")
    return value


class BearerUser(HttpUser):
    """
    Role load user with two safe authentication modes.

    Preferred for long/soak runs:
      SMARTEDU_PERF_<ROLE>_EMAIL / _PASSWORD
      -> login via Identity
      -> refresh using the Sprint 18 HttpOnly cookie on 401

    Optional for short smoke runs:
      SMARTEDU_<ROLE>_TOKEN
    """

    abstract = True
    wait_time = between(1.0, 5.0)
    token_env = ""
    credential_prefix = ""

    def on_start(self) -> None:
        self.access_token = ""
        token = env(self.token_env)
        if token:
            self._set_access_token(token)
            return

        email = env(f"{self.credential_prefix}_EMAIL")
        password = env(f"{self.credential_prefix}_PASSWORD")
        if not email or not password:
            raise StopUser(
                f"Provide {self.token_env} or "
                f"{self.credential_prefix}_EMAIL/_PASSWORD"
            )

        with self.client.post(
            "/api/v1/identity/auth/login",
            name="auth.login.background",
            json={"email": email, "password": password},
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"login failed: {response.status_code} "
                    f"{response.text[:200]}"
                )
                raise StopUser("Performance user login failed")

            payload = response.json()
            token = payload.get("access_token") or payload.get("accessToken")
            if not isinstance(token, str) or not token:
                response.failure("login response missing access token")
                raise StopUser("Performance user login response invalid")
            self._set_access_token(token)

    def _set_access_token(self, token: str) -> None:
        self.access_token = token
        self.client.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
        )

    def _refresh(self) -> bool:
        # HttpSession preserves the HttpOnly refresh cookie exactly as a browser
        # would. The Origin header satisfies Sprint 18 cookie-action protection.
        origin = env("SMARTEDU_FRONTEND_ORIGIN", "http://localhost:3000")
        with self.client.post(
            "/api/v1/identity/auth/refresh",
            name="auth.refresh.background",
            json={},
            headers={"Origin": origin, "X-Requested-With": "XMLHttpRequest"},
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"refresh failed: {response.status_code} "
                    f"{response.text[:200]}"
                )
                return False

            payload = response.json()
            token = payload.get("access_token") or payload.get("accessToken")
            if not isinstance(token, str) or not token:
                response.failure("refresh response missing access token")
                return False
            self._set_access_token(token)
            return True

    def get_json(self, path: str, *, name: str, _retried: bool = False):
        with self.client.get(
            path,
            name=name,
            catch_response=True,
        ) as response:
            if response.status_code == 401 and not _retried and self._refresh():
                response.success()
                return self.get_json(path, name=name, _retried=True)

            if response.status_code != 200:
                response.failure(
                    f"{response.status_code}: {response.text[:200]}"
                )
            return response

    def mutate_json(
        self,
        method: str,
        path: str,
        *,
        name: str,
        payload: dict[str, Any],
        _retried: bool = False,
    ):
        headers = {"Idempotency-Key": str(uuid.uuid4())}
        with self.client.request(
            method,
            path,
            name=name,
            json=payload,
            headers=headers,
            catch_response=True,
        ) as response:
            if response.status_code == 401 and not _retried and self._refresh():
                response.success()
                return self.mutate_json(
                    method,
                    path,
                    name=name,
                    payload=payload,
                    _retried=True,
                )

            if response.status_code not in {200, 201, 202, 204}:
                response.failure(
                    f"{response.status_code}: {response.text[:200]}"
                )
            return response
