"""Run real browser tests without exposing generated demo credentials."""
import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
secrets = json.loads((ROOT / ".integration/runtime/secrets.json").read_text())
env = {**os.environ, "SMARTEDU_FRONTEND_URL": "http://localhost:5173", "SMARTEDU_BROWSER_CHANNEL": os.environ.get("SMARTEDU_BROWSER_CHANNEL", "chrome"), "SMARTEDU_E2E_VIDEO": "false", "SMARTEDU_E2E_LOGIN_PACING_MS": "7000"}
for role in ("student", "teacher", "admin"):
    env[f"SMARTEDU_E2E_{role.upper()}_EMAIL"] = f"{role}@demo.example.edu"
    env[f"SMARTEDU_E2E_{role.upper()}_PASSWORD"] = secrets["DEMO_PASSWORD"] if role == "admin" else secrets[f"{role.upper()}_PASSWORD"]
command = [str(ROOT / "tests/e2e/node_modules/.bin/playwright.cmd"), "test", "--workers=1"] if os.name == "nt" else ["npx", "playwright", "test", "--workers=1"]
fixtures = json.loads((ROOT / ".integration/runtime/demo-fixtures.json").read_text())
with httpx.Client(base_url="http://localhost:18080", timeout=20) as client:
    response = client.post("/api/v1/identity/auth/login", json={
        "email": "teacher@demo.example.edu", "password": secrets["TEACHER_PASSWORD"],
    }, headers={"Origin": "http://localhost:5173"})
    if response.status_code != 200:
        raise SystemExit(f"E2E fixture login HTTP {response.status_code}")
    headers = {"Authorization": f"Bearer {response.json()['access_token']}", "Origin": "http://localhost:5173"}

    def create(path, payload):
        result = client.post("/api/v1/assessments/" + path, json=payload, headers=headers)
        if result.status_code not in (200, 201, 202):
            raise SystemExit(f"E2E fixture creation HTTP {result.status_code}")
        return result.json()

    for duration, variable, title in (
        (15, "SMARTEDU_E2E_ASSIGNMENT_ID", "Demo QA · Browser saved progress"),
        (1, "SMARTEDU_E2E_TIMED_ASSIGNMENT_ID", "Demo QA · Browser timed assessment"),
    ):
        quiz = create("quizzes", {"title": title, "course_id": fixtures["course"]["id"], "duration_minutes": duration})
        create(f"quizzes/{quiz['id']}/questions", {"question_id": fixtures["question"]["id"]})
        create(f"quizzes/{quiz['id']}/publish", {})
        current = datetime.now(UTC)
        assignment = create(f"quizzes/{quiz['id']}/assignments", {
            "section_id": fixtures["section"]["id"],
            "opens_at": (current - timedelta(minutes=1)).isoformat(),
            "due_at": (current + timedelta(hours=1)).isoformat(),
        })
        env[variable] = assignment["id"]
raise SystemExit(subprocess.run(command, cwd=ROOT / "tests/e2e", env=env).returncode)
