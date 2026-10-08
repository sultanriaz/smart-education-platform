"""Measure the existing sprint workload against the private local gateway.

500 virtual users share three labelled demo identities; this is a local
engineering measurement, not institutional workload acceptance or a claim of
production capacity. Edge throttles stay enabled.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import date, timedelta

import httpx
import yaml

from local_stack import ROOT, RUNTIME


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("smoke", "srs-500"), default="smoke")
    args = parser.parse_args()
    profile = next(row for row in yaml.safe_load((ROOT / "tests/performance/config/load-profiles.yaml").read_text())["profiles"] if row["name"] == args.profile)
    secrets = json.loads((RUNTIME / "secrets.json").read_text())
    env = {**os.environ, "PYTHONPATH": str(ROOT / "tests/performance/locust"), "SMARTEDU_FRONTEND_ORIGIN": "http://localhost:5173"}
    with httpx.Client(base_url="http://localhost:18080", timeout=20) as client:
        for role in ("student", "teacher", "admin"):
            password = secrets["DEMO_PASSWORD"] if role == "admin" else secrets[f"{role.upper()}_PASSWORD"]
            response = client.post("/api/v1/identity/auth/login", json={"email": f"{role}@demo.example.edu", "password": password})
            if response.status_code != 200:
                raise SystemExit(f"Performance setup login {role}: HTTP {response.status_code}")
            env[f"SMARTEDU_{role.upper()}_TOKEN"] = response.json()["access_token"]
    query = f"?start_date={date.today().isoformat()}&end_date={(date.today()+timedelta(days=13)).isoformat()}"
    env["PERF_STUDENT_SCHEDULE_PATH"] = env["PERF_TEACHER_SCHEDULE_PATH"] = "/api/v1/scheduling/timetable/me" + query
    output = ROOT / "artifacts/performance"
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{args.profile}-environment.json").write_text(json.dumps({"profile": profile, "gateway": "localhost:18080", "identities": 3, "virtual_users": profile["users"], "edge_throttles": "enabled", "acceptance": "Local diagnostic; institutional workload/hardware not approved", "frontend_build": "production"}, indent=2))
    command = [sys.executable, "-m", "locust", "-f", "tests/performance/locust/locustfile.py", "StudentUser", "TeacherUser", "AdminUser", "--headless", "--host", "http://127.0.0.1:18080", "-u", str(profile["users"]), "-r", str(profile["spawn_rate"]), "-t", str(profile["duration_seconds"]) + "s", "--csv", str(output / args.profile), "--html", str(output / f"{args.profile}.html"), "--exit-code-on-error", "1"]
    return subprocess.run(command, cwd=ROOT, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
