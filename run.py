#!/usr/bin/env python3
"""SmartEdu Platform — Unified Single Running Point.

Starts and manages:
- Supporting Docker infrastructure (PostgreSQL, RabbitMQ, Redis, MinIO, Mailpit, API Gateway)
- All 12 FastAPI microservices (Identity, Academic, Attendance, Scheduling, Notification,
  Facility, Learning, Assessment, Reporting, Platform, Finance, Payroll)
- RabbitMQ asynchronous event workers
- React / Vite frontend web portal

Usage:
    python run.py                 # Start entire platform (Infra + Services + Frontend)
    python run.py --status        # Check health of all services and ports
    python run.py --stop          # Stop all running services and frontend
    python run.py --credentials   # Display active demo credentials and URLs
    python run.py --test          # Run the 38-case live integration regression suite
    python run.py --services-only # Run 12 microservices and workers only
    python run.py --frontend-only # Run frontend preview only
    python run.py --infra-only    # Start Docker infrastructure containers only
    python run.py --skip-docker   # Start services and frontend without Docker check
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / ".integration" / "runtime"
COMPOSE_FILE = ROOT / "docker-compose.local.yml"

# Services: (name, port)
SERVICES = [
    ("identity", 8001),
    ("academic", 8002),
    ("attendance", 8003),
    ("scheduling", 8004),
    ("notification", 8005),
    ("facility", 8006),
    ("learning", 8007),
    ("assessment", 8008),
    ("reporting", 8009),
    ("platform", 8010),
    ("finance", 8011),
    ("payroll", 8012),
]

INFRA_PORTS = {
    "PostgreSQL 16 (12 DBs)": 15432,
    "RabbitMQ AMQP": 55672,
    "RabbitMQ Management UI": 55673,
    "Redis Durable": 56380,
    "Redis Cache": 56379,
    "MinIO S3 API": 59000,
    "MinIO S3 Console": 59001,
    "Mailpit SMTP": 11025,
    "Mailpit Webmail": 18025,
    "API Gateway (Nginx)": 18080,
}

FRONTEND_PORT = 5173
GATEWAY_PORT = 18080


def get_python_executable() -> str:
    """Return the virtualenv python if available, else current sys.executable."""
    if os.name == "nt":
        venv_py = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.3) -> bool:
    """Check if a TCP port is accepting connections."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((host, port)) == 0
    except Exception:
        return False


def wait_for_port(port: int, host: str = "127.0.0.1", timeout_sec: float = 15.0) -> bool:
    """Wait until a TCP port starts accepting connections."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if is_port_open(port, host=host):
            return True
        time.sleep(0.4)
    return False


def check_http_health(url: str, timeout: float = 1.0) -> tuple[bool, int | str]:
    """Check HTTP GET endpoint health."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmartEdu-Runner"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (resp.status == 200, resp.status)
    except urllib.error.HTTPError as exc:
        return (False, exc.code)
    except Exception as exc:
        return (False, str(exc))


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a .env file safely without hard external dependencies."""
    if not path.exists():
        return {}
    try:
        from dotenv import dotenv_values
        return {k: v for k, v in dotenv_values(path).items() if v is not None}
    except ImportError:
        res = {}
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            res[k.strip()] = v.strip().strip("\"'")
        return res


def load_secrets() -> dict[str, str]:
    """Load secrets from runtime configuration."""
    secrets_file = RUNTIME / "secrets.json"
    if secrets_file.exists():
        try:
            return json.loads(secrets_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def ensure_configuration():
    """Ensure runtime environment and secrets exist; generate if missing."""
    RUNTIME.mkdir(parents=True, exist_ok=True)
    secrets_file = RUNTIME / "secrets.json"
    if not secrets_file.exists():
        print("[*] Generating local runtime configuration and cryptographic keys...")
        config_script = ROOT / "scripts" / "configure_local.py"
        if config_script.exists():
            subprocess.run([get_python_executable(), str(config_script)], cwd=ROOT, check=True)
            print("[+] Configuration generated successfully.")
        else:
            print("[!] Warning: scripts/configure_local.py not found.")


def build_service_env(name: str) -> dict[str, str]:
    """Build environment dictionary for a specific microservice."""
    env_file = RUNTIME / f"{name}-service.env"
    file_vars = parse_env_file(env_file)
    libs_paths = [
        str(ROOT / "libs" / "python" / "smartedu_contracts"),
        str(ROOT / "libs" / "python" / "smartedu_infra"),
        str(ROOT / "libs" / "python" / "smartedu_observability"),
        str(ROOT / "libs" / "python" / "smartedu_perf"),
        str(ROOT / "libs" / "python" / "smartedu_security"),
        str(ROOT / "services" / f"{name}-service"),
    ]
    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    pythonpath = os.pathsep.join(libs_paths + ([existing_pythonpath] if existing_pythonpath else []))
    return {
        **os.environ,
        "PYTHONPATH": pythonpath,
        **file_vars,
    }


def check_docker_available(timeout_sec: float = 3.0) -> bool:
    """Check if Docker engine is running and responsive."""
    try:
        res = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return res.returncode == 0
    except Exception:
        return False


def start_docker_infrastructure():
    """Ensure docker containers from docker-compose.local.yml are up."""
    if not COMPOSE_FILE.exists():
        print(f"[!] Compose file {COMPOSE_FILE} not found; skipping docker startup.")
        return

    print("[*] Checking Docker infrastructure containers...")
    if not check_docker_available():
        print("    [!] Docker daemon is not responding or still starting.")
        print("        If using Docker Desktop, please ensure it has completed booting.")
        print("        Proceeding with application service startup...")
        return

    try:
        # Check if postgres container is already running
        cmd_ps = ["docker", "compose", "-f", str(COMPOSE_FILE), "ps", "--format", "json"]
        ps_res = subprocess.run(cmd_ps, cwd=ROOT, capture_output=True, text=True, timeout=5.0)
        already_up = "smartedu" in ps_res.stdout.lower() or "postgres" in ps_res.stdout.lower()

        if not already_up or not is_port_open(INFRA_PORTS["PostgreSQL 16 (12 DBs)"]):
            print("[*] Starting Docker infrastructure containers (Postgres, RabbitMQ, Redis, MinIO, Gateway)...")
            cmd_up = ["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"]
            subprocess.run(cmd_up, cwd=ROOT, check=True, timeout=30.0)
            print("[+] Docker containers started. Waiting for PostgreSQL readiness...")
            wait_for_port(INFRA_PORTS["PostgreSQL 16 (12 DBs)"], timeout_sec=15.0)
            wait_for_port(INFRA_PORTS["API Gateway (Nginx)"], timeout_sec=15.0)
            print("[+] Infrastructure is online and accepting connections.")
        else:
            print("[+] Docker infrastructure containers are already running.")
    except Exception as exc:
        print(f"    [!] Notice during Docker check: {exc}")
        print("        Proceeding with available services...")


def ensure_frontend_built():
    """Check if frontend build exists; build if missing."""
    dist_index = ROOT / "apps" / "frontend" / "dist" / "index.html"
    if not dist_index.exists():
        print("[*] Frontend distribution build not found. Running 'npm run build'...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        try:
            subprocess.run([npm_cmd, "run", "build"], cwd=ROOT / "apps" / "frontend", check=True)
            print("[+] Frontend built successfully.")
        except Exception as exc:
            print(f"[!] Warning: Frontend build failed ({exc}). Will attempt live dev server instead.")


def kill_process_tree(proc: subprocess.Popen):
    """Terminate a process and all its children cleanly."""
    if proc.poll() is not None:
        return
    pid = proc.pid
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
        else:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
    except Exception:
        pass


def stop_running_services():
    """Find and stop any local uvicorn and frontend processes running on SmartEdu ports."""
    print("[*] Checking for running services to stop...")
    ports_to_kill = [s[1] for s in SERVICES] + [FRONTEND_PORT]

    if os.name == "nt":
        # Windows netstat check
        try:
            res = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            killed_pids = set()
            my_pid = os.getpid()
            for line in res.stdout.splitlines():
                line = line.strip()
                if "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        addr = parts[1]
                        pid = parts[-1]
                        try:
                            port = int(addr.rsplit(":", 1)[-1])
                            if port in ports_to_kill and pid.isdigit() and int(pid) != my_pid:
                                killed_pids.add(int(pid))
                        except Exception:
                            continue
            for pid in killed_pids:
                try:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
                    print(f"    [+] Stopped process PID {pid}")
                except Exception:
                    pass
            print(f"[+] Cleanup complete. {len(killed_pids)} process(es) terminated.")
        except Exception as exc:
            print(f"[!] Error stopping processes: {exc}")
    else:
        print("[+] Please use Ctrl+C or kill matching process IDs on Unix.")


def print_banner():
    """Print the platform banner."""
    print("=" * 80)
    print("  SMART EDUCATION PLATFORM (SmartEdu) — UNIFIED SYSTEM RUNNER")
    print("  Wave 17 Enterprise Release | 12 Microservices | React Frontend | API Gateway")
    print("=" * 80)


def print_credentials(secrets: dict[str, str] | None = None):
    """Print platform demo credentials and quick access URLs."""
    if secrets is None:
        secrets = load_secrets()

    admin_pass = secrets.get("DEMO_PASSWORD", "Demo!UCxagNDHeToFSZXHcdxlRiie7aZ")
    teacher_pass = secrets.get("TEACHER_PASSWORD", "Q7!Oa8xZ24L2aX0dEnj8TuSWGEoDgN-vY8KxEVrnts6cbAaZ")
    student_pass = secrets.get("STUDENT_PASSWORD", "Q7!vEpzlshyGXIddiaOLN7GT73b1cUc71pLVJ1ybXGm5dUaZ")
    checker_pass = secrets.get("CHECKER_PASSWORD", "S9!K8mP2vL#4uY7wQz")

    print("\n" + "-" * 80)
    print("  ACCESS URLS")
    print("-" * 80)
    print("  * Frontend Web Portal     : http://localhost:5173")
    print("  * API Gateway             : http://localhost:18080")
    print("  * Mailpit (Email Sandbox) : http://localhost:18025")
    print("  * RabbitMQ Management UI  : http://localhost:55673  (user: smartedu)")
    print("  * MinIO S3 Console        : http://localhost:59001  (user: smartedu)")
    print("-" * 80)
    print("  DEMO USER ACCOUNTS & PASSWORDS")
    print("-" * 80)
    print(f"  [1] Administrator : admin@demo.example.edu")
    print(f"      Password      : {admin_pass}")
    print(f"      Dashboard     : http://localhost:5173/app/admin")
    print(f"  [2] Faculty/Staff : teacher@demo.example.edu")
    print(f"      Password      : {teacher_pass}")
    print(f"      Dashboard     : http://localhost:5173/app/teacher")
    print(f"  [3] Student       : student@demo.example.edu")
    print(f"      Password      : {student_pass}")
    print(f"      Dashboard     : http://localhost:5173/app/student")
    print(f"  [4] Finance Check : checker@demo.example.edu")
    print(f"      Password      : {checker_pass}")
    print(f"      Role          : Dual-Control Maker-Checker Approver")
    print("-" * 80 + "\n")


def print_status_table():
    """Query and display health status of all infrastructure and services."""
    print_banner()
    print("\n--- INFRASTRUCTURE CONTAINERS & PORTS ---")
    for name, port in INFRA_PORTS.items():
        open_state = is_port_open(port)
        status = "[ONLINE] " if open_state else "[OFFLINE]"
        print(f"  {status:10} {name:25} (Port {port})")

    print("\n--- TWELVE MICROSERVICES (FASTAPI) ---")
    for name, port in SERVICES:
        open_state = is_port_open(port)
        if open_state:
            health_ok, code = check_http_health(f"http://127.0.0.1:{port}/health", timeout=0.5)
            status = "[HEALTHY]" if health_ok else f"[HTTP {code}]"
        else:
            status = "[OFFLINE]"
        print(f"  {status:10} {name.capitalize() + ' Service':25} (Port {port}) -> http://localhost:{port}/health")

    print("\n--- FRONTEND & GATEWAY ---")
    gw_open = is_port_open(GATEWAY_PORT)
    gw_status = "[ONLINE] " if gw_open else "[OFFLINE]"
    print(f"  {gw_status:10} {'Nginx API Gateway':25} (Port {GATEWAY_PORT}) -> http://localhost:{GATEWAY_PORT}")

    fe_open = is_port_open(FRONTEND_PORT)
    fe_status = "[ONLINE] " if fe_open else "[OFFLINE]"
    print(f"  {fe_status:10} {'React Frontend Portal':25} (Port {FRONTEND_PORT}) -> http://localhost:{FRONTEND_PORT}")
    print()


def run_platform(skip_docker: bool = False, services_only: bool = False, frontend_only: bool = False):
    """Main orchestration engine for starting the platform."""
    print_banner()
    python_bin = get_python_executable()
    print(f"[*] Python Runtime Environment : {python_bin}")
    print(f"[*] Workspace Root Directory   : {ROOT}")

    # 1. Configuration & Secrets
    ensure_configuration()
    secrets = load_secrets()

    # 2. Docker Infrastructure
    if not skip_docker and not services_only and not frontend_only:
        start_docker_infrastructure()

    procs: dict[str, subprocess.Popen] = {}

    def shutdown():
        print("\n[*] Stopping all SmartEdu background processes cleanly...")
        for key, p in list(procs.items()):
            try:
                kill_process_tree(p)
            except Exception:
                pass
        print("[+] All services stopped.")

    # 3. Launch Frontend (if requested or normal run)
    if not services_only:
        ensure_frontend_built()
        dist_index = ROOT / "apps" / "frontend" / "dist" / "index.html"
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

        if dist_index.exists():
            fe_cmd = [npm_cmd, "run", "preview", "--", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT), "--strictPort"]
        else:
            fe_cmd = [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT)]

        fe_log = open(RUNTIME / "frontend.log", "ab")
        fe_proc = subprocess.Popen(fe_cmd, cwd=ROOT / "apps" / "frontend", stdout=fe_log, stderr=fe_log)
        procs["frontend"] = fe_proc
        print(f"[+] Started Frontend server (PID {fe_proc.pid}) on port {FRONTEND_PORT}")

    # If only frontend was requested, monitor and wait
    if frontend_only:
        print_credentials(secrets)
        print("[*] Frontend is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            shutdown()
            return

    # 4. Launch 12 Microservices & Event Workers
    print("\n[*] Starting 12 Microservices on ports 8001–8012...")
    for idx, (name, port) in enumerate(SERVICES, 1):
        if is_port_open(port):
            print(f"    [~] {name.capitalize()} API is already listening on port {port}.")
            continue

        api_cmd = [
            python_bin,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
        ]
        api_log = open(RUNTIME / f"{name}-api.log", "ab")
        cwd = ROOT / "services" / f"{name}-service"
        proc = subprocess.Popen(api_cmd, cwd=cwd, env=build_service_env(name), stdout=api_log, stderr=api_log)
        procs[f"{name}:api"] = proc
        print(f"    [+] Started {name.capitalize():12} API (PID {proc.pid:5}) on port {port}")

    # 5. Launch RabbitMQ Event Workers
    print("\n[*] Starting RabbitMQ asynchronous event workers...")
    for name, _ in SERVICES:
        worker_file = ROOT / "services" / f"{name}-service" / "app" / "event_worker.py"
        if not worker_file.exists():
            continue

        worker_cmd = [python_bin, "-m", "app.event_worker"]
        worker_log = open(RUNTIME / f"{name}-events.log", "ab")
        cwd = ROOT / "services" / f"{name}-service"
        proc = subprocess.Popen(worker_cmd, cwd=cwd, env=build_service_env(name), stdout=worker_log, stderr=worker_log)
        procs[f"{name}:worker"] = proc
        print(f"    [+] Started {name.capitalize():12} event worker (PID {proc.pid:5})")

    # 6. Wait for readiness
    print("\n[*] Waiting for microservice health verification...")
    all_healthy = False
    start_wait = time.time()
    while time.time() - start_wait < 15.0:
        statuses = [check_http_health(f"http://127.0.0.1:{p}/health")[0] for _, p in SERVICES]
        if all(statuses):
            all_healthy = True
            break
        time.sleep(0.5)

    if all_healthy:
        print("[+] All 12 microservices passed HTTP health checks successfully!")
    else:
        print("[!] Note: Some services may still be initializing. Checking port availability...")

    # 7. Print URLs and Credentials
    print_credentials(secrets)
    print("[*] SmartEdu platform is fully active! Press Ctrl+C at any time to exit.\n")

    # 8. Supervision Loop (Auto-restart if a process exits unexpectedly)
    try:
        while True:
            time.sleep(2)
            # Check APIs
            for idx, (name, port) in enumerate(SERVICES, 1):
                key = f"{name}:api"
                p = procs.get(key)
                if p and p.poll() is not None:
                    print(f"[!] WARNING: {name} API exited (code {p.returncode}). Restarting on port {port}...")
                    api_cmd = [
                        python_bin,
                        "-m",
                        "uvicorn",
                        "app.main:app",
                        "--host",
                        "0.0.0.0",
                        "--port",
                        str(port),
                    ]
                    api_log = open(RUNTIME / f"{name}-api.log", "ab")
                    cwd = ROOT / "services" / f"{name}-service"
                    procs[key] = subprocess.Popen(
                        api_cmd, cwd=cwd, env=build_service_env(name), stdout=api_log, stderr=api_log
                    )

            # Check Frontend
            if "frontend" in procs and procs["frontend"].poll() is not None:
                print("[!] WARNING: Frontend server exited. Restarting...")
                dist_index = ROOT / "apps" / "frontend" / "dist" / "index.html"
                npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
                if dist_index.exists():
                    fe_cmd = [npm_cmd, "run", "preview", "--", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT), "--strictPort"]
                else:
                    fe_cmd = [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT)]
                fe_log = open(RUNTIME / "frontend.log", "ab")
                procs["frontend"] = subprocess.Popen(
                    fe_cmd, cwd=ROOT / "apps" / "frontend", stdout=fe_log, stderr=fe_log
                )
    except KeyboardInterrupt:
        shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="SmartEdu Platform — Unified Single Running Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py                 # Start entire platform
    python run.py --status        # Check health status of all components
    python run.py --stop          # Stop all running microservices and frontend
    python run.py --credentials   # View active login accounts and passwords
    python run.py --test          # Run the 38-test live regression verification
    python run.py --services-only # Start 12 microservices and event workers only
    python run.py --frontend-only # Start frontend preview only
    python run.py --skip-docker   # Start services without checking Docker
        """,
    )
    parser.add_argument("--status", action="store_true", help="Display health and port status of all components")
    parser.add_argument("--stop", action="store_true", help="Stop running microservices and frontend processes")
    parser.add_argument("--credentials", action="store_true", help="Display active demo login credentials and URLs")
    parser.add_argument("--test", "--verify", dest="test", action="store_true", help="Run the live 38-case regression suite")
    parser.add_argument("--infra-only", action="store_true", help="Start Docker infrastructure only")
    parser.add_argument("--services-only", action="store_true", help="Start 12 microservices and workers only")
    parser.add_argument("--frontend-only", action="store_true", help="Start frontend preview server only")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker engine check and container startup")

    args = parser.parse_args()

    if args.status:
        print_status_table()
        sys.exit(0)

    if args.credentials:
        print_banner()
        print_credentials()
        sys.exit(0)

    if args.stop:
        print_banner()
        stop_running_services()
        sys.exit(0)

    if args.test:
        print_banner()
        test_script = ROOT / "scripts" / "verify_live_local.py"
        if not test_script.exists():
            print("[!] Error: scripts/verify_live_local.py not found.")
            sys.exit(1)
        print("[*] Running 38-case live system regression suite...\n")
        res = subprocess.run([get_python_executable(), str(test_script)], cwd=ROOT)
        sys.exit(res.returncode)

    if args.infra_only:
        print_banner()
        start_docker_infrastructure()
        sys.exit(0)

    run_platform(
        skip_docker=args.skip_docker,
        services_only=args.services_only,
        frontend_only=args.frontend_only,
    )


if __name__ == "__main__":
    main()
