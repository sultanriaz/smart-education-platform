# Smart Education Platform

An integrated final-year project with ten independent Python/FastAPI services, a React/TypeScript frontend, and Student, Teacher, and Admin workspaces. Each service owns its database. HTTP contracts and durable domain events connect services.

The local demonstration uses PostgreSQL, two authenticated Redis instances, RabbitMQ, private MinIO storage, Mailpit, and Nginx. It uses generated private credentials and labelled demo records. Draft as-built requirements are in [docs/requirements](docs/requirements/AS_BUILT_SYSTEM_REQUIREMENTS.md); they are not an approved SRS.

## Windows PowerShell

Prerequisites: Python 3.12 (`py -3.12`), Node.js 24/npm, Git, Docker Desktop with the Linux engine running, and Google Chrome for the local browser runner. Run from this repository. Initial dependency and source-image downloads require network access.

```powershell
Set-Location C:\black_paper\Projects\smart-education-platform
# 1. Install dependencies and generate isolated local configuration
.\scripts\local.ps1 -Action Configure
# 2. Start this project's infrastructure, gateway and private storage
.\scripts\local.ps1 -Action Infrastructure
# 3. Apply migrations to each service's own database
.\scripts\local.ps1 -Action Migrate
# 4. Start ten APIs, verify readiness, then start their owned event workers
.\scripts\local.ps1 -Action Services
# 5. Seed labelled demonstration records through the owner APIs
.\scripts\local.ps1 -Action Seed
# 6. Build and start the production frontend preview
.\scripts\local.ps1 -Action Frontend
# 7. Open the application
Start-Process 'http://localhost:5173'
# 8. Run suites, frontend lint/build, live workflows and browser/accessibility checks
.\scripts\local.ps1 -Action Test
# 9. Stop only recorded local processes and this Docker project; retain volumes
.\scripts\local.ps1 -Action Stop
```

If PowerShell blocks local scripts, invoke them with `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action Configure` (and the desired action). This does not change the machine execution policy. Seeding requires responding APIs, so Services precedes Seed.

Demo emails: `admin@demo.example.edu`, `teacher@demo.example.edu`, `student@demo.example.edu`. Inspect the ignored `.integration/runtime/secrets.json` locally: `DEMO_PASSWORD` is Admin's password; the other roles use `TEACHER_PASSWORD` and `STUDENT_PASSWORD`. Do not commit or distribute that file. Configure preserves existing credentials and service `.env` files.

Frontend: `http://localhost:5173`; gateway: `http://localhost:18080`; local email viewer: `http://localhost:18025`. Windows reserves 8080 on the verification machine. Native API ports 8001–8010 follow Identity, Academic, Attendance, Scheduling, Notification, Facility, Learning, Assessment, Reporting, Platform. Infrastructure host ports: PostgreSQL 55432, cache Redis 56379, durable Redis 56380, RabbitMQ 55672/55673, MinIO 59000/59001, SMTP 11025. Frontend and gateway ports are part of the generated local CORS/cookie configuration.

## Verification and development

```powershell
.venv\Scripts\python.exe scripts\local_stack.py status
.venv\Scripts\python.exe scripts\verify_local.py
.venv\Scripts\python.exe scripts\verify_live_local.py
.venv\Scripts\python.exe scripts\run_local_e2e.py
.venv\Scripts\python.exe scripts\run_local_performance.py --profile smoke
.venv\Scripts\python.exe scripts\run_local_performance.py --profile srs-500
.venv\Scripts\python.exe scripts\inspect_local_query_plans.py
.venv\Scripts\python.exe scripts\secret_scan.py --strict
.venv\Scripts\python.exe scripts\container_security_audit.py --strict
# Optional: build all ten Linux service images using the verified wheel cache
.venv\Scripts\python.exe scripts\build_local_images.py --prepare
# Start disposable containers and verify health, owned migrations and authenticated APIs
.venv\Scripts\python.exe scripts\verify_local_images.py
Push-Location apps\frontend
npm run lint
npm run test -- --run
npm run build
Pop-Location
```

Run load tests separately from browser timing checks. The local load runner uses three demo identities and leaves edge security limits enabled. Its result does not establish institutional acceptance or production capacity. For development, stop the recorded frontend and run `npm run dev -- --host 127.0.0.1 --port 5173 --strictPort` in `apps/frontend`.

Python dependency versions are constrained to the locally tested set in `requirements.constraints.txt`. The optional image helper downloads Linux wheels on the host with package hash validation, then builds the normal service recipes using that cache. Normal root-context Dockerfiles can also install directly from the package index. Container verification removes only its randomly named temporary containers and preserves all volumes. Browser checks create fresh labelled assessment fixtures, including a real one-minute expiry case, so repeated runs do not exhaust a Student's demonstration attempt quota.

Logs/private PID records: `.integration/runtime`. Test evidence/screenshots/load reports: `artifacts`. These directories are ignored. Original sprint archives are retained locally; imports are recorded in [the inventory](docs/integration/SPRINT_INVENTORY.md). Do not rerun archive overlays over the repaired integration.

See [the delivery report](docs/integration/FINAL_DELIVERY_REPORT.md) for actual PASS/FAIL/SKIPPED/NOT RUN results and remaining external gates. Staging, production, institutional UAT, accepted disaster-recovery objectives, sustained availability, and release approval require their real environments and owners.
