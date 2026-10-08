"""Start, migrate or stop only the generated local integration environment."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".integration/runtime"
NAMES = [
    "identity",
    "academic",
    "attendance",
    "scheduling",
    "notification",
    "facility",
    "learning",
    "assessment",
    "reporting",
    "platform",
]


def environment(name):
    return {
        **os.environ,
        **{
            key: value
            for key, value in dotenv_values(RUNTIME / f"{name}-service.env").items()
            if value is not None
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=["migrate", "start", "status", "stop", "workers", "frontend"]
    )
    args = parser.parse_args()
    if not (RUNTIME / "secrets.json").exists():
        raise SystemExit("Run scripts/configure_local.py first.")
    if args.action == "migrate":
        for name in NAMES:
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=ROOT / f"services/{name}-service",
                env=environment(name),
            )
            if result.returncode:
                raise SystemExit(result.returncode)
        return
    pidfile = RUNTIME / "processes.json"
    records = json.loads(pidfile.read_text()) if pidfile.exists() else []
    if args.action == "frontend":
        import psutil

        for record in records:
            if record["kind"] != "frontend":
                continue
            try:
                process = psutil.Process(record["pid"])
                if abs(process.create_time() - record["started"]) < 5:
                    print("Recorded frontend already running")
                    return
            except psutil.NoSuchProcess:
                pass
        command = (
            [
                "cmd",
                "/c",
                "npm.cmd",
                "run",
                "preview",
                "--",
                "--host",
                "127.0.0.1",
                "--port",
                "5173",
                "--strictPort",
            ]
            if os.name == "nt"
            else [
                "npm",
                "run",
                "preview",
                "--",
                "--host",
                "127.0.0.1",
                "--port",
                "5173",
                "--strictPort",
            ]
        )
        with (RUNTIME / "frontend.log").open("ab") as log:
            process = subprocess.Popen(
                command,
                cwd=ROOT / "apps/frontend",
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        records.append(
            {
                "pid": process.pid,
                "service": "frontend",
                "kind": "frontend",
                "started": time.time(),
            }
        )
        pidfile.write_text(json.dumps(records, indent=2))
        print("Started production frontend preview at http://localhost:5173")
        return
    if args.action in {"start", "workers"}:
        for index, name in enumerate(NAMES, 1):
            kind = "api" if args.action == "start" else "events"
            if kind == "events":
                import psutil

                active = False
                for record in records:
                    if record["service"] != name or record["kind"] != kind:
                        continue
                    try:
                        process = psutil.Process(record["pid"])
                        active = (
                            abs(process.create_time() - record["started"]) < 5
                            and "app.event_worker" in process.cmdline()
                        )
                    except psutil.NoSuchProcess:
                        pass
                    if active:
                        break
                if active:
                    print(f"{name}: event worker already running", flush=True)
                    continue
            url = f"http://127.0.0.1:{8000 + index}/health"
            if kind == "api":
                try:
                    httpx.get(url, timeout=1).raise_for_status()
                    print(f"{name}: already responding", flush=True)
                    continue
                except httpx.HTTPError:
                    pass
            elif not (ROOT / f"services/{name}-service/app/event_worker.py").exists():
                continue
            command = (
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(8000 + index),
                ]
                if kind == "api"
                else [sys.executable, "-m", "app.event_worker"]
            )
            logfile = RUNTIME / f"{name}-{kind}.log"
            with logfile.open("ab") as log:
                process = subprocess.Popen(
                    command,
                    cwd=ROOT / f"services/{name}-service",
                    env=environment(name),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
            records.append(
                {
                    "pid": process.pid,
                    "service": name,
                    "kind": kind,
                    "started": time.time(),
                }
            )
            pidfile.write_text(json.dumps(records, indent=2))
            print(
                f"Started {name} {kind}; log: {logfile.relative_to(ROOT)}", flush=True
            )
        return
    if args.action == "status":
        failed = False
        for index, name in enumerate(NAMES, 1):
            try:
                response = httpx.get(
                    f"http://127.0.0.1:{8000 + index}/health", timeout=3
                )
                status = str(response.status_code)
                failed |= response.status_code != 200
            except httpx.HTTPError:
                status, failed = "unavailable", True
            try:
                readiness = httpx.get(
                    f"http://127.0.0.1:{8000 + index}/ready", timeout=5
                ).status_code
                failed |= readiness != 200
            except httpx.HTTPError:
                readiness, failed = "unavailable", True
            print(f"{name}: health={status} ready={readiness}", flush=True)
        raise SystemExit(int(failed))
    # Resolve and check process creation time before stopping; PID reuse must
    # never terminate an unrelated application.
    import psutil

    for record in records:
        try:
            process = psutil.Process(record["pid"])
            if abs(process.create_time() - record["started"]) > 5:
                continue
            if not any(
                "uvicorn" in arg or "app.event_worker" in arg
                for arg in process.cmdline()
            ):
                if record["kind"] != "frontend" or not any(
                    "preview" == arg for arg in process.cmdline()
                ):
                    continue
                for child in process.children(recursive=True):
                    child.terminate()
            process.terminate()
            process.wait(timeout=10)
        except psutil.NoSuchProcess:
            pass
    pidfile.write_text("[]")
    print(
        "Stopped recorded local service processes. Databases and Docker volumes preserved."
    )


if __name__ == "__main__":
    main()
