"""Exercise disposable service containers against this project's infrastructure."""

import json
import socket
import subprocess
import time
import uuid
from datetime import date, timedelta
from pathlib import Path

import httpx
from dotenv import dotenv_values
from local_stack import NAMES, ROOT, RUNTIME
from sqlalchemy.engine import make_url


def main():
    run_id = uuid.uuid4().hex[:8]
    created, endpoints, records = [], {}, []
    paths = {
        "identity": "/users/me",
        "academic": "/students/me/sections",
        "attendance": "/students/me/attendance/summary",
        "scheduling": f"/timetable/me?start_date={date.today()}&end_date={date.today() + timedelta(days=13)}",
        "notification": "/notifications",
        "facility": "/facilities",
        "learning": "/students/me/resources",
        "assessment": "/students/me/assignments",
        "reporting": "/dashboard/overview",
        "platform": "/admin/settings",
    }
    output = ROOT / "artifacts/verification/container-results.json"
    secrets = json.loads((RUNTIME / "secrets.json").read_text())
    try:
        for name in NAMES:
            env = {
                key: value
                for key, value in dotenv_values(RUNTIME / f"{name}-service.env").items()
                if value is not None
            }
            env["DATABASE_URL"] = (
                make_url(env["DATABASE_URL"])
                .set(host="infra-postgres", port=5432)
                .render_as_string(hide_password=False)
            )
            for key, value in list(env.items()):
                for before, after in (
                    ("127.0.0.1:56379", "redis-cache:6379"),
                    ("127.0.0.1:56380", "redis-durable:6379"),
                    ("127.0.0.1:55672", "rabbitmq:5672"),
                    ("127.0.0.1:59000", "minio:9000"),
                ):
                    value = value.replace(before, after)
                env[key] = value
            env.update(
                {
                    "JWT_JWKS_URL": "http://identity-api:8000/.well-known/jwks.json",
                    "ACADEMIC_SERVICE_BASE_URL": "http://academic-api:8000",
                    "IDENTITY_SERVICE_BASE_URL": "http://identity-api:8000",
                    "NOTIFICATION_SERVICE_BASE_URL": "http://notification-api:8000",
                    "SMTP_HOST": "mailpit",
                    "SMTP_PORT": "1025",
                    "TRUSTED_HOSTS": "localhost,127.0.0.1,"
                    + ",".join(f"{service}-api" for service in NAMES),
                }
            )
            # Mount only this owner's private service key; Identity also needs
            # its own RSA signing key. Public verification material is shared.
            mounts = []
            for key in (
                "INTERNAL_SERVICE_PRIVATE_KEY_FILE",
                "JWT_PRIVATE_KEY_FILE",
                "JWT_PUBLIC_KEY_FILE",
            ):
                if key in env:
                    source = Path(env[key]).resolve()
                    assert source.is_relative_to(RUNTIME.resolve())
                    target = f"/run/local-keys/{source.name}"
                    env[key] = target
                    mounts += [
                        "--mount",
                        f"type=bind,src={source},dst={target},readonly",
                    ]
            envfile = RUNTIME / f"image-{name}.env"
            envfile.write_text(
                "\n".join(f"{key}={value}" for key, value in env.items()) + "\n",
                encoding="utf-8",
            )
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            container = f"smartedu-image-check-{name}-{run_id}"
            command = [
                "docker",
                "run",
                "-d",
                "--name",
                container,
                "--label",
                "smartedu.purpose=image-verification",
                "--network",
                "smartedu-local-backend",
                "--network-alias",
                f"{name}-api",
                "--env-file",
                str(envfile),
                "-p",
                f"127.0.0.1:{port}:8000",
                *mounts,
                f"smartedu-local/{name}-service:integration",
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
            created.append(container)
            endpoints[name] = f"http://127.0.0.1:{port}"
        with httpx.Client(timeout=10) as client:
            for name in NAMES:
                ready = False
                for _ in range(30):
                    try:
                        ready = all(
                            client.get(endpoints[name] + f"/{path}").status_code == 200
                            for path in ("health", "ready")
                        )
                    except httpx.HTTPError:
                        pass
                    if ready:
                        break
                    time.sleep(1)
                record = {
                    "service": name,
                    "status": "PASS" if ready else "FAIL",
                    "checks": "Real container health and owned migration readiness",
                }
                records.append(record)
                output.write_text(json.dumps(records, indent=2))
                if not ready:
                    log = subprocess.run(["docker", "logs", next(container for container in created if f"image-check-{name}-" in container)], capture_output=True, text=True, encoding="utf-8", errors="replace")
                    (RUNTIME / f"image-{name}-failure.log").write_text(log.stdout + log.stderr, encoding="utf-8")
                    raise RuntimeError(f"{name} container failed readiness")
            tokens = {}
            for role in ("student", "admin"):
                password = (
                    secrets["DEMO_PASSWORD"]
                    if role == "admin"
                    else secrets["STUDENT_PASSWORD"]
                )
                response = client.post(
                    endpoints["identity"] + "/api/v1/auth/login",
                    json={"email": f"{role}@demo.example.edu", "password": password},
                )
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Container {role} login HTTP {response.status_code}"
                    )
                tokens[role] = response.json()["access_token"]
            for record in records:
                name = record["service"]
                token = tokens[
                    "admin"
                    if name in {"identity", "reporting", "platform"}
                    else "student"
                ]
                response = client.get(
                    endpoints[name] + "/api/v1" + paths[name],
                    headers={"Authorization": f"Bearer {token}"},
                )
                record["api_status"] = response.status_code
                record["status"] = "PASS" if response.status_code == 200 else "FAIL"
                print(
                    f"{name}: container health/readiness and authenticated owner API {record['status']}",
                    flush=True,
                )
                output.write_text(json.dumps(records, indent=2))
        return int(any(record["status"] == "FAIL" for record in records))
    finally:
        # These names were created in this invocation with a random suffix.
        # No unrelated container or persistent volume is removed.
        for container in reversed(created):
            subprocess.run(["docker", "rm", "-f", container], capture_output=True)


if __name__ == "__main__":
    raise SystemExit(main())
