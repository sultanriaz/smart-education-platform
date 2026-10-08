"""Run real browser tests without exposing generated demo credentials."""
import os
import subprocess
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
secrets = json.loads((ROOT / ".integration/runtime/secrets.json").read_text())
env = {**os.environ, "SMARTEDU_FRONTEND_URL": "http://localhost:5173", "SMARTEDU_BROWSER_CHANNEL": os.environ.get("SMARTEDU_BROWSER_CHANNEL", "chrome"), "SMARTEDU_E2E_VIDEO": "false", "SMARTEDU_E2E_LOGIN_PACING_MS": "7000"}
for role in ("student", "teacher", "admin"):
    env[f"SMARTEDU_E2E_{role.upper()}_EMAIL"] = f"{role}@demo.example.edu"
    env[f"SMARTEDU_E2E_{role.upper()}_PASSWORD"] = secrets["DEMO_PASSWORD"] if role == "admin" else secrets[f"{role.upper()}_PASSWORD"]
command = [str(ROOT / "tests/e2e/node_modules/.bin/playwright.cmd"), "test", "--workers=1"] if os.name == "nt" else ["npx", "playwright", "test", "--workers=1"]
fixtures = json.loads((ROOT / ".integration/runtime/demo-fixtures.json").read_text())
env["SMARTEDU_E2E_ASSIGNMENT_ID"] = fixtures["assessment-assignment"]["id"]
raise SystemExit(subprocess.run(command, cwd=ROOT / "tests/e2e", env=env).returncode)
