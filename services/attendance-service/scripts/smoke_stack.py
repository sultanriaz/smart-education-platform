"""Disposable Docker integration check using the real Academic API and public JWKS.

Run from repository root with Attendance's Python environment. No existing service
containers, signing keys, or development databases are read or modified.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

ROOT = Path(__file__).resolve().parents[3]


def docker(*args: str) -> str:
    return subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def wait_ready(base_url: str, path: str = "/ready") -> None:
    deadline = time.monotonic() + 30
    with httpx.Client(timeout=2) as client:
        while time.monotonic() < deadline:
            try:
                if client.get(base_url + path).status_code == 200:
                    return
            except httpx.RequestError:
                pass
            time.sleep(0.2)
    raise RuntimeError(f"Service did not become ready: {base_url}")


def main() -> None:
    for name in ("academic", "attendance"):
        subprocess.run(
            [
                "docker",
                "build",
                "--quiet",
                "--tag",
                f"smart-education-{name}:smoke",
                str(ROOT / "services" / f"{name}-service"),
            ],
            check=True,
        )
    prefix = f"attendance-smoke-{uuid4().hex[:8]}"
    network = prefix + "-network"
    containers: list[str] = []
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key(), as_dict=True)
    public.update(kid="smoke-key", alg="RS256", use="sig")
    stub = """from __future__ import annotations
from http.server import BaseHTTPRequestHandler, HTTPServer
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(PAYLOAD)
    def log_message(self, *args):
        pass
HTTPServer(('0.0.0.0', 8001), Handler).serve_forever()
""".replace("PAYLOAD", repr(json.dumps({"keys": [public]}).encode("utf-8")))
    with tempfile.NamedTemporaryFile(
        prefix="attendance_smoke_", suffix=".py", delete=False
    ) as file:
        file.write(stub.encode("utf-8"))
        stub_path = Path(file.name).resolve()
    assert stub_path.is_relative_to(Path(tempfile.gettempdir()).resolve())

    def run(name: str, *args: str) -> str:
        container = prefix + "-" + name
        docker("run", "--detach", "--name", container, "--network", network, *args)
        containers.append(container)
        return container

    def url(container: str, port: str = "8000/tcp") -> str:
        info = json.loads(docker("inspect", container))[0]
        binding = info["NetworkSettings"]["Ports"][port][0]
        return f"http://127.0.0.1:{binding['HostPort']}"

    def bearer(user_id, roles):
        now = int(datetime.now(UTC).timestamp())
        token = jwt.encode(
            {
                "sub": str(user_id),
                "roles": roles,
                "iss": "http://localhost:8001",
                "aud": "smart-education-api",
                "type": "access",
                "jti": uuid4().hex,
                "iat": now,
                "nbf": now,
                "exp": now + 900,
            },
            key,
            algorithm="RS256",
            headers={"typ": "at+jwt", "kid": "smoke-key"},
        )
        return {"Authorization": f"Bearer {token}"}

    try:
        docker("network", "create", network)
        jwks = run(
            "jwks",
            "--publish",
            "127.0.0.1::8001",
            "--mount",
            f"type=bind,source={stub_path},target=/smoke.py,readonly",
            "smart-education-attendance:smoke",
            "python",
            "/smoke.py",
        )
        wait_ready(url(jwks, "8001/tcp"), "/.well-known/jwks.json")
        databases = {}
        for name in ("academic", "attendance"):
            database = run(
                name + "-db",
                "--env",
                f"POSTGRES_DB={name}_test_smoke",
                "--env",
                "POSTGRES_USER=smoke",
                "--env",
                "POSTGRES_PASSWORD=smoke",
                "postgres:16",
            )
            databases[name] = database
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        database,
                        "pg_isready",
                        "-U",
                        "smoke",
                        "-d",
                        f"{name}_test_smoke",
                    ],
                    capture_output=True,
                )
                if result.returncode == 0:
                    break
                time.sleep(0.2)
            else:
                raise RuntimeError("Disposable PostgreSQL did not become ready.")
            docker(
                "run",
                "--rm",
                "--network",
                network,
                "--env",
                f"DATABASE_URL=postgresql+psycopg://smoke:smoke@{database}:5432/{name}_test_smoke",
                f"smart-education-{name}:smoke",
                "alembic",
                "upgrade",
                "head",
            )
        academic_container = run(
            "academic-api",
            "--publish",
            "127.0.0.1::8000",
            "--env",
            f"DATABASE_URL=postgresql+psycopg://smoke:smoke@{databases['academic']}:5432/academic_test_smoke",
            "--env",
            f"JWT_JWKS_URL=http://{jwks}:8001/.well-known/jwks.json",
            "smart-education-academic:smoke",
        )
        attendance_container = run(
            "attendance-api",
            "--publish",
            "127.0.0.1::8000",
            "--env",
            f"DATABASE_URL=postgresql+psycopg://smoke:smoke@{databases['attendance']}:5432/attendance_test_smoke",
            "--env",
            f"JWT_JWKS_URL=http://{jwks}:8001/.well-known/jwks.json",
            "--env",
            f"ACADEMIC_SERVICE_BASE_URL=http://{academic_container}:8000",
            "smart-education-attendance:smoke",
        )
        academic_url, attendance_url = url(academic_container), url(attendance_container)
        wait_ready(academic_url)
        wait_ready(attendance_url)
        admin = bearer(uuid4(), ["admin"])
        teacher_id = uuid4()
        student_ids = [uuid4(), uuid4()]
        teacher = bearer(teacher_id, ["teacher"])
        student = bearer(student_ids[0], ["student"])
        with httpx.Client(timeout=15) as client:

            def create(path, payload):
                response = client.post(
                    academic_url + "/api/v1/" + path, headers=admin, json=payload
                )
                assert response.status_code == 201, (path, response.text)
                return response.json()

            department = create("departments", {"code": "CS", "name": "Computing"})
            program = create(
                "programs",
                {
                    "code": "BSCS",
                    "name": "Computer Science",
                    "duration_semesters": 8,
                    "department_id": department["id"],
                },
            )
            year = create(
                "academic-years",
                {
                    "code": "2026",
                    "name": "2026/27",
                    "starts_on": "2026-08-01",
                    "ends_on": "2027-07-31",
                },
            )
            semester = create(
                "semesters",
                {
                    "academic_year_id": year["id"],
                    "number": 1,
                    "name": "Fall",
                    "starts_on": "2026-08-15",
                    "ends_on": "2026-12-31",
                },
            )
            course = create(
                "courses",
                {
                    "program_id": program["id"],
                    "code": "CS101",
                    "title": "Computing",
                    "credits": 3,
                    "semester_number": 1,
                },
            )
            section = create(
                "sections",
                {
                    "course_id": course["id"],
                    "semester_id": semester["id"],
                    "code": "A",
                    "capacity": 10,
                },
            )
            profile = create(
                "teacher-profiles",
                {
                    "external_user_id": str(teacher_id),
                    "employee_number": "T1",
                    "department_id": department["id"],
                    "designation": "Lecturer",
                },
            )
            create(
                "teacher-assignments",
                {"teacher_profile_id": profile["id"], "section_id": section["id"]},
            )
            for index, user_id in enumerate(student_ids):
                profile = create(
                    "student-profiles",
                    {
                        "external_user_id": str(user_id),
                        "student_number": f"S{index}",
                        "program_id": program["id"],
                        "admission_year_id": year["id"],
                        "current_semester": 1,
                    },
                )
                create(
                    "enrollments",
                    {"student_profile_id": profile["id"], "section_id": section["id"]},
                )
            for path in ("/health", "/ready", "/openapi.json"):
                response = client.get(attendance_url + path)
                assert response.status_code == 200, (path, response.text)
            response = client.post(
                attendance_url + "/api/v1/sessions",
                headers=teacher,
                json={"section_id": section["id"], "session_date": "2026-10-07"},
            )
            assert response.status_code == 201, response.text
            session_url = attendance_url + "/api/v1/sessions/" + response.json()["id"]
            records_url = session_url + "/records"
            payload = {
                "records": [
                    {"student_user_id": str(student_ids[0]), "status": "PRESENT"},
                    {"student_user_id": str(student_ids[1]), "status": "ABSENT"},
                ]
            }
            response = client.put(records_url, headers=teacher, json=payload)
            assert response.status_code == 200, response.text
            assert client.post(session_url + "/finalize", headers=teacher).status_code == 200
            own = client.get(
                attendance_url + "/api/v1/students/me/attendance", headers=student
            ).json()
            assert len(own) == 1 and own[0]["student_user_id"] == str(student_ids[0])
            summary = client.get(
                attendance_url + "/api/v1/students/me/attendance/summary", headers=student
            ).json()
            assert summary["totals"]["attendance_percentage"] == 100.0
            assert summary["by_course"][0]["course_id"] == course["id"]
            assert client.get(records_url, headers=student).status_code == 403
            assert client.get(records_url, headers=bearer(uuid4(), ["teacher"])).status_code == 403
            correction = {"status": "EXCUSED", "reason": "Authorized historical correction"}
            assert (
                client.patch(
                    records_url + f"/{student_ids[1]}", headers=teacher, json=correction
                ).status_code
                == 409
            )
            assert (
                client.patch(
                    records_url + f"/{student_ids[1]}", headers=admin, json=correction
                ).status_code
                == 200
            )
            assert (
                len(client.get(records_url + f"/{student_ids[1]}/history", headers=admin).json())
                == 1
            )
            docker("rm", "--force", academic_container)
            assert client.get(records_url, headers=teacher).status_code == 503
            assert client.get(records_url, headers=admin).status_code == 200
            assert (
                client.get(
                    attendance_url + "/api/v1/students/me/attendance", headers=student
                ).status_code
                == 200
            )
            assert client.get(attendance_url + "/ready").status_code == 200
            assert docker("exec", attendance_container, "id", "-u") == "10001"
            print(
                "PASS: Docker health/readiness/OpenAPI; real Academic assignment/roster checks; "
                "teacher marking/finalization; student self-access; corrections/history; "
                "dependency outage policy; non-root runtime."
            )
    finally:
        for container in reversed(containers):
            subprocess.run(["docker", "rm", "--force", "--volumes", container], capture_output=True)
        subprocess.run(["docker", "network", "rm", network], capture_output=True)
        stub_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
