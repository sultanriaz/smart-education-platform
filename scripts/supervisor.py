"""Supervisor daemon to manage all 12 SmartEdu services and event workers under Windows."""
from __future__ import annotations

import os
import sys
import time
import subprocess
from pathlib import Path
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
    "finance",
    "payroll",
]


def environment(name: str) -> dict[str, str]:
    env_file = RUNTIME / f"{name}-service.env"
    file_vars = dotenv_values(env_file) if env_file.exists() else {}
    return {
        **os.environ,
        **{k: v for k, v in file_vars.items() if v is not None},
    }


def main():
    print(f"Starting supervisor for {len(NAMES)} services...", flush=True)
    procs: dict[str, subprocess.Popen] = {}

    def start_api(name: str, index: int):
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(8000 + index),
        ]
        log = open(RUNTIME / f"{name}-api.log", "ab")
        cwd = ROOT / f"services/{name}-service"
        proc = subprocess.Popen(cmd, cwd=cwd, env=environment(name), stdout=log, stderr=log)
        procs[f"{name}:api"] = proc
        print(f"Started {name} API (pid={proc.pid}) on port {8000 + index}", flush=True)

    def start_events(name: str):
        worker_file = ROOT / f"services/{name}-service/app/event_worker.py"
        if not worker_file.exists():
            return
        cmd = [sys.executable, "-m", "app.event_worker"]
        log = open(RUNTIME / f"{name}-events.log", "ab")
        cwd = ROOT / f"services/{name}-service"
        proc = subprocess.Popen(cmd, cwd=cwd, env=environment(name), stdout=log, stderr=log)
        procs[f"{name}:events"] = proc
        print(f"Started {name} event worker (pid={proc.pid})", flush=True)

    def start_frontend():
        cmd = ["npm.cmd", "run", "preview", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"] if os.name == "nt" else ["npm", "run", "preview", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"]
        log = open(RUNTIME / "frontend.log", "ab")
        cwd = ROOT / "apps/frontend"
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=log, stderr=log)
        procs["frontend"] = proc
        print(f"Started frontend preview (pid={proc.pid}) on port 5173", flush=True)

    # Launch APIs
    for idx, name in enumerate(NAMES, 1):
        start_api(name, idx)

    # Launch Event Workers
    for name in NAMES:
        start_events(name)

    # Launch Frontend
    start_frontend()

    print("All services, workers, and frontend launched. Monitoring...", flush=True)

    try:
        while True:
            time.sleep(2)
            # Restart any unexpectedly exited API process
            for idx, name in enumerate(NAMES, 1):
                key = f"{name}:api"
                p = procs.get(key)
                if p and p.poll() is not None:
                    print(f"WARNING: {name} API exited with code {p.returncode}. Restarting...", flush=True)
                    start_api(name, idx)

            if "frontend" in procs and procs["frontend"].poll() is not None:
                print("WARNING: frontend exited. Restarting...", flush=True)
                start_frontend()
    except KeyboardInterrupt:
        print("Stopping all services...", flush=True)
        for key, p in procs.items():
            try:
                p.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()

