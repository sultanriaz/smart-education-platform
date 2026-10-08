from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

SERVICES = [
    "identity-service",
    "academic-service",
    "attendance-service",
    "scheduling-service",
    "notification-service",
    "facility-service",
    "learning-service",
    "assessment-service",
    "reporting-service",
    "platform-service",
]


def env_password_name(service: str) -> str:
    return "RABBITMQ_" + service.removesuffix("-service").replace("-", "_").upper() + "_PASSWORD"


def request(
    method: str,
    url: str,
    *,
    username: str,
    password: str,
    payload: dict | None = None,
) -> None:
    body = None if payload is None else json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    basic = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers["Authorization"] = f"Basic {basic}"
    req = urllib.request.Request(
        url,
        method=method,
        data=body,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status >= 300:
                raise RuntimeError(f"RabbitMQ API returned {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(
            f"RabbitMQ API {method} {url} failed: {exc.code} {detail}"
        ) from exc


def main() -> None:
    management_url = os.getenv(
        "RABBITMQ_MANAGEMENT_URL",
        "http://localhost:15672",
    ).rstrip("/")
    admin_user = os.getenv("RABBITMQ_BOOTSTRAP_USER", "smartedu")
    admin_password = os.environ["RABBITMQ_BOOTSTRAP_PASSWORD"]
    vhost = os.getenv("RABBITMQ_VHOST", "smartedu")
    queue_prefix = os.getenv("EVENT_QUEUE_PREFIX", "smartedu")

    encoded_vhost = urllib.parse.quote(vhost, safe="")
    queue_prefix_regex = re.escape(queue_prefix)

    for service in SERVICES:
        user = service.removesuffix("-service").replace("-", "_") + "_svc"
        password = os.environ[env_password_name(service)]

        request(
            "PUT",
            f"{management_url}/api/users/{urllib.parse.quote(user, safe='')}",
            username=admin_user,
            password=admin_password,
            payload={"password": password, "tags": ""},
        )

        service_regex = re.escape(service)
        own_queue = (
            rf"^{queue_prefix_regex}\.{service_regex}\.events"
            rf"(?:\.retry|\.dlq)?$"
        )
        write_exchanges = r"^smartedu\.(?:events|retry|dlx)$"

        request(
            "PUT",
            (
                f"{management_url}/api/permissions/{encoded_vhost}/"
                f"{urllib.parse.quote(user, safe='')}"
            ),
            username=admin_user,
            password=admin_password,
            payload={
                "configure": own_queue,
                "write": write_exchanges,
                "read": own_queue,
            },
        )
        print(f"Configured RabbitMQ least-privilege user {user}")


if __name__ == "__main__":
    main()
