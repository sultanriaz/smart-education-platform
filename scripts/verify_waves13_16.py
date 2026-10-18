"""Actual pass/fail evidence runner for the implemented Waves 13–16 portion.

Does NOT assert the 266-scenario catalog has run, or bypass missing tools.
Use --full for identity, backend, UI and live-Waves-0-12 regression gates.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBS = [ROOT / "libs" / "python" / pkg for pkg in ("smartedu_infra", "smartedu_contracts", "smartedu_security", "smartedu_observability", "smartedu_testkit")]


def run_step(name: str, args: list[str], *, cwd: Path, timeout=480):
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(map(str, LIBS)) + os.pathsep + str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        completed = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)
        text = (completed.stdout + "\n" + completed.stderr)[-8000:]
        return {"name": name, "pass": completed.returncode == 0, "exit_code": completed.returncode, "command": args, "output_tail": text}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"name": name, "pass": False, "error": f"{type(exc).__name__}: {exc}", "command": args}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Enforce full repo and integration gates")
    opts = parser.parse_args()
    records = []
    suites = {
        "platform": ["test_wave13_14_governance.py", "test_settings_jobs.py", "test_support.py", "test_events_search_audit.py", "test_durable_jobs.py"],
        "reporting": ["test_wave15_parity.py", "test_exports.py", "test_dashboard.py"],
    }
    for service, names in suites.items():
        cwd = ROOT / "services" / f"{service}-service"
        paths = [str(Path("tests") / name) for name in names]
        records.append(run_step(f"{service}_focused", [sys.executable, "-m", "pytest", "-q", *paths], cwd=cwd))
    if opts.full:
        for service in ("identity", "academic", "platform", "reporting"):
            cwd = ROOT / "services" / f"{service}-service"
            records.append(run_step(f"{service}_full", [sys.executable, "-m", "pytest", "-q", "tests"], cwd=cwd, timeout=900))
        npm = "npm.cmd" if os.name == "nt" else "npm"
        records.append(run_step("frontend_build", [npm, "run", "build"], cwd=ROOT / "apps" / "frontend", timeout=900))
        records.append(run_step("waves00_12_live", [sys.executable, str(ROOT / "scripts" / "verify_live_local.py")], cwd=ROOT, timeout=900))
    dest = ROOT / ".integration" / "runtime" / "waves13_16"
    dest.mkdir(parents=True, exist_ok=True)
    artifact = {"generated_at": datetime.now(UTC).isoformat(), "mode": "full" if opts.full else "focused", "overall_pass": all(record["pass"] for record in records), "runs": records, "not_verified": ["266-scenario acceptance", "WCAG manual evidence", "pilot signatories", "staging capacity", "real alert delivery", "DB restore/swap"]}
    (dest / "verification.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    for record in records:
        print(("PASS " if record["pass"] else "FAIL ") + record["name"])
    print("Evidence:", dest / "verification.json")
    return 0 if artifact["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
