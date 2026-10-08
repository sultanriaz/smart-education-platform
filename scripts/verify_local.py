"""Run isolated suites; never import ten unrelated 'app' packages in one process."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    suites = list(sorted((ROOT / "services").glob("*-service"))) + list(sorted((ROOT / "libs/python").glob("smartedu_*"))) + [ROOT / "infra/gateway", ROOT]
    results = []
    output = ROOT / "artifacts/verification"
    output.mkdir(parents=True, exist_ok=True)
    previous = json.loads((output / "results.json").read_text()) if args.only and (output / "results.json").exists() else []
    for directory in suites:
        name = directory.name if directory != ROOT else "system"
        if args.only and name not in args.only:
            continue
        env = {**os.environ, "ENVIRONMENT": "test", "TRACING_ENABLED": "false", "TRUSTED_HOSTS": "localhost,127.0.0.1,testserver", "PYTHONIOENCODING": "utf-8"}
        cmd = [sys.executable, "-m", "pytest", "tests", "-q", "--tb=short"]
        start = time.monotonic()
        try:
            result = subprocess.run(cmd, cwd=directory, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
            text = result.stdout + result.stderr
            status = "PASS" if result.returncode == 0 else "FAIL"
        except subprocess.TimeoutExpired as exc:
            text, status = str(exc), "FAIL"
        (output / f"{name}.log").write_text(text, encoding="utf-8")
        record = {"component": name, "command": " ".join(cmd), "environment": "Python 3.12 isolated local suite; live checks require explicit test configuration", "status": status, "seconds": round(time.monotonic() - start, 2), "summary": text.strip().splitlines()[-1] if text.strip() else "No output"}
        results.append(record)
        print(f"{name}: {status}: {record['summary']}", flush=True)
        merged = {record["component"]: record for record in previous + results}
        (output / "results.json").write_text(json.dumps(list(merged.values()), indent=2), encoding="utf-8")
    lines = ["# Test results", "", "Executed locally; skipped live cases in each log remain SKIPPED, never implied PASS.", "", "| Component | Suite result | Duration | Output |", "|---|---|---:|---|"]
    records = {record["component"]: record for record in previous + results}
    lines += [f"| {r['component']} | {r['status']} | {r['seconds']}s | {r['summary'].replace('|', '/')} |" for r in records.values()]
    lines += ["", "Exact commands/environment: `artifacts/verification/results.json`. Full failure reasons and skip reasons: `artifacts/verification/<component>.log`."]
    (ROOT / "docs/integration/TEST_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return int(any(r["status"] == "FAIL" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
