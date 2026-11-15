#!/usr/bin/env python3
"""SmartEdu Platform — Unified Single Running Point (General / Non-Docker).

This is a general, standalone runner that does NOT require Docker.
It runs:
- Native Python API Gateway on port 18080 (routing to downstream microservices with full CORS)
- All 12 FastAPI microservices (Identity, Academic, Attendance, Scheduling, Notification,
  Facility, Learning, Assessment, Reporting, Platform, Finance, Payroll) on ports 8001–8012
- React / Vite frontend web portal on port 5173
- RabbitMQ event workers (when RabbitMQ is locally present)

Usage:
    python run.py                 # Start entire platform (Gateway + Services + Frontend)
    python run.py --status        # Check health and status of all services and ports
    python run.py --stop          # Stop all running services, gateway, and frontend
    python run.py --credentials   # Display active demo credentials and URLs
    python run.py --test          # Run the 38-case live integration regression suite
    python run.py --services-only # Run 12 microservices only (without frontend)
    python run.py --frontend-only # Run frontend preview only
    python run.py --gateway-only  # Run native Python API Gateway only
    python run.py --with-docker   # Optionally start Docker infrastructure containers if installed
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import signal
import socket
import subprocess
import sys
import threading
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

ROUTE_MAP = {
    "identity": 8001,
    "academic": 8002,
    "attendance": 8003,
    "scheduling": 8004,
    "notification": 8005,
    "notifications": 8005,
    "facility": 8006,
    "facilities": 8006,
    "learning": 8007,
    "assessment": 8008,
    "assessments": 8008,
    "reporting": 8009,
    "platform": 8010,
    "finance": 8011,
    "payroll": 8012,
}

FRONTEND_PORT = 5173
GATEWAY_PORT = 18080


# ==============================================================================
# Helper Utilities
# ==============================================================================

def get_python_executable() -> str:
    """Return the virtualenv python if available, else current sys.executable."""
    if os.name == "nt":
        venv_py = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.25) -> bool:
    """Check if a TCP port is currently listening."""
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
        time.sleep(0.3)
    return False


def check_http_health(url: str, timeout: float = 0.5) -> tuple[bool, int | str]:
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
    """Parse a .env file safely without external dependencies."""
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
    """Stop any local processes running on SmartEdu ports."""
    print("[*] Checking for running services to stop...")
    ports_to_kill = [s[1] for s in SERVICES] + [FRONTEND_PORT, GATEWAY_PORT]

    if os.name == "nt":
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


# ==============================================================================
# Native Python API Gateway (Port 18080)
# ==============================================================================

class SmartEduGatewayHandler(http.server.BaseHTTPRequestHandler):
    """Native Python reverse proxy routing to downstream microservices."""

    def log_message(self, format, *args):
        # Suppress verbose standard output; log to file if needed
        pass

    def send_cors_headers(self):
        origin = self.headers.get("Origin", "http://localhost:5173")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Authorization, Content-Type, Accept, Idempotency-Key, X-Requested-With, X-Request-ID, X-Correlation-ID, traceparent, tracestate",
        )
        self.send_header(
            "Access-Control-Expose-Headers",
            "X-Request-ID, X-Correlation-ID, X-Service-Name, X-Idempotent-Replay, Set-Cookie",
        )

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self._proxy("GET")

    def do_POST(self):
        self._proxy("POST")

    def do_PUT(self):
        self._proxy("PUT")

    def do_PATCH(self):
        self._proxy("PATCH")

    def do_DELETE(self):
        self._proxy("DELETE")

    def _proxy(self, method: str):
        path = self.path
        if path in ("/health", "/ready"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"native-api-gateway"}')
            return

        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"service":"smart-education-api-gateway","status":"ok"}')
            return

        upstream_url = self._resolve_upstream(path)
        if not upstream_url:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"detail":"Route not found on API gateway"}')
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        forward_headers = {}
        for key, val in self.headers.items():
            if key.lower() not in ("host", "connection", "content-length"):
                forward_headers[key] = val

        req = urllib.request.Request(upstream_url, data=body, headers=forward_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() in ("transfer-encoding", "content-encoding", "access-control-allow-origin", "set-cookie"):
                        continue
                    self.send_header(k, v)
                for cookie in resp.headers.get_all("Set-Cookie") or []:
                    self.send_header("Set-Cookie", cookie)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as exc:
            self.send_response(exc.code)
            for k, v in exc.headers.items():
                if k.lower() in ("transfer-encoding", "content-encoding", "access-control-allow-origin", "set-cookie"):
                    continue
                self.send_header(k, v)
            for cookie in exc.headers.get_all("Set-Cookie") or []:
                self.send_header("Set-Cookie", cookie)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(exc.read())
        except Exception as exc:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            err_msg = json.dumps({"detail": f"Upstream service connection failed: {exc}"}).encode("utf-8")
            self.wfile.write(err_msg)

    @staticmethod
    def _resolve_upstream(path: str) -> str | None:
        clean_path = path.split("?", 1)[0]
        query_string = path.split("?", 1)[1] if "?" in path else ""
        parts = clean_path.lstrip("/").split("/")
        if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
            svc = parts[2]
            if svc in ROUTE_MAP:
                port = ROUTE_MAP[svc]
                rest = "/".join(parts[3:])
                if rest in ("health", "ready"):
                    target = f"http://127.0.0.1:{port}/{rest}"
                else:
                    target = f"http://127.0.0.1:{port}/api/v1/{rest}"
                if query_string:
                    target += f"?{query_string}"
                return target
        return None


def start_native_gateway(port: int = GATEWAY_PORT) -> http.server.ThreadingHTTPServer | None:
    """Start the native Python gateway on port 18080 if not already open."""
    if is_port_open(port):
        print(f"    [+] API Gateway is already listening on port {port}.")
        return None

    try:
        server = http.server.ThreadingHTTPServer(("0.0.0.0", port), SmartEduGatewayHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[+] Started Native Python API Gateway on http://localhost:{port}")
        return server
    except Exception as exc:
        print(f"[!] Warning: Could not start native API Gateway on port {port}: {exc}")
        return None


# ==============================================================================
# Banners & Reporting
# ==============================================================================

def print_banner():
    """Print the platform banner."""
    print("=" * 80)
    print("  SMART EDUCATION PLATFORM (SmartEdu) — GENERAL SYSTEM RUNNER")
    print("  Standalone / Native Execution | 12 Microservices | React Frontend | API Gateway")
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
    print("  * RabbitMQ Management UI  : http://localhost:55673")
    print("  * MinIO S3 Console        : http://localhost:59001")
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
    print(f"  {gw_status:10} {'API Gateway':25} (Port {GATEWAY_PORT}) -> http://localhost:{GATEWAY_PORT}")

    fe_open = is_port_open(FRONTEND_PORT)
    fe_status = "[ONLINE] " if fe_open else "[OFFLINE]"
    print(f"  {fe_status:10} {'React Frontend Portal':25} (Port {FRONTEND_PORT}) -> http://localhost:{FRONTEND_PORT}")

    print("\n--- LOCAL INFRASTRUCTURE PORTS ---")
    pg_open = is_port_open(15432)
    print(f"  {'[ONLINE]' if pg_open else '[OFFLINE]':10} {'PostgreSQL Database':25} (Port 15432)")
    rmq_open = is_port_open(55672)
    print(f"  {'[ONLINE]' if rmq_open else '[OFFLINE]':10} {'RabbitMQ Message Broker':25} (Port 55672)")
    redis_open = is_port_open(56380)
    print(f"  {'[ONLINE]' if redis_open else '[OFFLINE]':10} {'Redis Durable Store':25} (Port 56380)")
    print()


# ==============================================================================
# Platform Orchestration
# ==============================================================================

def ensure_frontend_built():
    """Check if frontend build exists; build if missing."""
    dist_index = ROOT / "apps" / "frontend" / "dist" / "index.html"
    if not dist_index.exists():
        print("[*] Frontend distribution build not found. Building with 'npm run build'...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        try:
            subprocess.run([npm_cmd, "run", "build"], cwd=ROOT / "apps" / "frontend", check=True)
            print("[+] Frontend built successfully.")
        except Exception as exc:
            print(f"[!] Warning: Frontend build failed ({exc}). Will attempt dev mode instead.")


def run_platform(
    services_only: bool = False,
    frontend_only: bool = False,
    gateway_only: bool = False,
    with_docker: bool = False,
):
    """Main orchestration engine for starting the platform natively."""
    print_banner()
    python_bin = get_python_executable()
    print(f"[*] Python Runtime Environment : {python_bin}")
    print(f"[*] Workspace Root Directory   : {ROOT}")

    # 1. Configuration & Secrets
    ensure_configuration()
    secrets = load_secrets()

    # 2. Optional Docker Check (Only if user explicitly asked)
    if with_docker and COMPOSE_FILE.exists():
        print("[*] --with-docker flag passed. Starting Docker containers...")
        try:
            subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"], cwd=ROOT, check=True)
            print("[+] Docker infrastructure started.")
        except Exception as exc:
            print(f"[!] Docker startup failed: {exc}")

    # Check local database status
    if not is_port_open(15432):
        print("[i] Notice: PostgreSQL is not detected on port 15432.")
        print("    Application services will start in local standalone mode.")
    else:
        print("[+] PostgreSQL database detected on port 15432.")

    procs: dict[str, subprocess.Popen] = {}
    gateway_server = None

    def shutdown():
        print("\n[*] Stopping all SmartEdu background processes cleanly...")
        if gateway_server:
            try:
                gateway_server.shutdown()
            except Exception:
                pass
        for key, p in list(procs.items()):
            try:
                kill_process_tree(p)
            except Exception:
                pass
        print("[+] All services stopped.")

    # 3. Start Native API Gateway
    if not frontend_only:
        gateway_server = start_native_gateway(GATEWAY_PORT)

    if gateway_only:
        print(f"[*] Native API Gateway is running on port {GATEWAY_PORT}. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            shutdown()
            return

    # 4. Launch Frontend
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

    if frontend_only:
        print_credentials(secrets)
        print("[*] Frontend is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            shutdown()
            return

    # 5. Launch 12 Microservices
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

    # 6. Launch Event Workers (Only if RabbitMQ is present)
    has_rabbitmq = is_port_open(55672)
    if has_rabbitmq:
        print("\n[*] RabbitMQ detected. Starting asynchronous event workers...")
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
    else:
        print("\n[i] RabbitMQ not detected on port 55672. Skipping event workers for standalone run.")

    # 7. Wait for Microservice Readiness
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
        print("[!] Note: Services launched. Checking port availability...")

    # 8. Print URLs and Credentials
    print_credentials(secrets)
    print("[*] SmartEdu platform is active! Press Ctrl+C at any time to exit.\n")

    # 9. Supervision Loop
    try:
        while True:
            time.sleep(2)
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
        description="SmartEdu Platform — Standalone General System Runner (Non-Docker)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py                 # Start entire platform (Gateway + 12 Services + Frontend)
    python run.py --status        # Check health status of all components
    python run.py --stop          # Stop all running microservices and frontend
    python run.py --credentials   # View active login accounts and passwords
    python run.py --test          # Run the 38-test live regression verification
    python run.py --services-only # Start 12 microservices only
    python run.py --frontend-only # Start frontend preview only
    python run.py --gateway-only  # Start native Python API gateway only
    python run.py --with-docker   # Optionally start Docker infrastructure containers if installed
        """,
    )
    parser.add_argument("--status", action="store_true", help="Display health and port status of all components")
    parser.add_argument("--stop", action="store_true", help="Stop running microservices and frontend processes")
    parser.add_argument("--credentials", action="store_true", help="Display active demo login credentials and URLs")
    parser.add_argument("--test", "--verify", dest="test", action="store_true", help="Run the live 38-case regression suite")
    parser.add_argument("--services-only", action="store_true", help="Start 12 microservices only (without frontend)")
    parser.add_argument("--frontend-only", action="store_true", help="Start frontend preview server only")
    parser.add_argument("--gateway-only", action="store_true", help="Start native Python API gateway only")
    parser.add_argument("--with-docker", action="store_true", help="Start Docker infrastructure containers if Docker is installed")

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

    run_platform(
        services_only=args.services_only,
        frontend_only=args.frontend_only,
        gateway_only=args.gateway_only,
        with_docker=args.with_docker,
    )


if __name__ == "__main__":
    main()
