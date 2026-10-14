"""Safe B13/B01 local operations using EXISTING runtime service env files.

Do not run Configure, Seed (demo data), database migrations or docker volume changes.
Usage: python scripts/b13_b01_local_ops.py seed-permissions
       python scripts/b13_b01_local_ops.py facility-dry-run
       python scripts/b13_b01_local_ops.py facility-apply
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".integration" / "runtime"


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"seed-permissions", "facility-dry-run", "facility-apply"}:
        print(__doc__)
        return 2
    action = sys.argv[1]
    name = "identity" if action == "seed-permissions" else "scheduling"
    env_path = RUNTIME / f"{name}-service.env"
    if not env_path.is_file():
        print(f"ABORT: Missing runtime file {env_path}. No changes made.")
        return 2
    options = dotenv_values(env_path)
    if not options.get("DATABASE_URL"):
        print("ABORT: Service DATABASE_URL is missing. No changes made.")
        return 2
    env = dict(os.environ)
    env.update({k: v for k, v in options.items() if v is not None})
    if action != "seed-permissions" and not env.get("INTERNAL_SERVICE_TOKEN"):
        print("ABORT: Internal Facility authentication is not configured.")
        return 2
    package_root = ROOT / "libs" / "python"
    lib_paths = [str(p) for p in package_root.iterdir() if p.is_dir()]
    env["PYTHONPATH"] = os.pathsep.join([*lib_paths, env.get("PYTHONPATH", "")])
    service_dir = ROOT / "services" / f"{name}-service"
    if action == "seed-permissions":
        command = [sys.executable, "-m", "app.scripts.seed_b01_permissions"]
        print("Adding missing RBAC permission codes without removing existing grants (no demo reseeding)...", flush=True)
    else:
        command = [sys.executable, "-m", "app.scripts.reconcile_facility_reservations"]
        if action == "facility-apply":
            command.append("--apply")
        print(f"B13 Facility reconciliation mode: {action}", flush=True)
    return subprocess.run(command, cwd=service_dir, env=env, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
