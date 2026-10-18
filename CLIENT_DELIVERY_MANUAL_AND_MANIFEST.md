# SmartEdu Platform — Complete Client Delivery Manual & Package Manifest
## Wave 17 Enterprise Release | Twelve Microservices | React Frontend | API Gateway

---

# SECTION 1 — ZIP ARCHIVE MANIFEST & INVENTORY

### Archive Details
- **File Name**: `SmartEdu_Client_Delivery_Wave17.zip`
- **Location**: `C:\black_paper\Projects\SmartEdu_Client_Delivery_Wave17.zip`
- **Compressed Size**: `2.15 MB` (Uncompressed: `5.52 MB`, 61.1% savings)
- **Total Files**: `2,428`
- **SHA-256 Checksum**: `f7de9fd39204c543e9ea2ffd2c1331739e180ed3e3a3be59ae1438eaf40e9771`

### Root Directory Structure in Archive
```text
smart-education-platform/
├── CLIENT_DELIVERY_MANUAL_AND_MANIFEST.md   # This comprehensive guide & archive manifest
├── DELIVERY_GUIDE.md                        # Quickstart, installation & operator instructions
├── USER_MANUAL.md                           # End-user manual for Admin, Teacher, and Student roles
├── README.md                                # General project readme & architecture overview
├── docker-compose.yml                       # Production-grade service composition manifest
├── pytest.ini                               # Python test runner configuration
├── pyproject.toml                           # Python project build & tool specifications
│
├── apps/                                    # Frontend Web Applications
│   └── frontend/                            # React 18 / Vite 5 / TypeScript Web Portal
│       ├── src/                             # Source code (features, components, hooks, lib)
│       ├── public/                          # Static assets and runtime configurations
│       ├── package.json                     # NPM dependencies and scripts
│       ├── vite.config.ts                   # Vite bundler configuration
│       ├── tailwind.config.ts               # Tailwind CSS design system configuration
│       └── tsconfig*.json                   # TypeScript compiler configurations
│
├── services/                                # Twelve Independent FastAPI Microservices
│   ├── identity-service/                    # Authentication, JWT rotation, user lifecycle
│   ├── academic-service/                    # Departments, programs, courses, sections, rosters
│   ├── attendance-service/                  # Attendance sessions, bulk marking, audit summary
│   ├── scheduling-service/                  # Class timetables, recurring occurrences
│   ├── notification-service/                # RabbitMQ announcements, preferences, emails
│   ├── facility-service/                    # Campus room & lab bookings, overlap rejection
│   ├── learning-service/                    # Educational resources, versioned private S3 files
│   ├── assessment-service/                  # Questions, timed quiz attempts, auto-grading
│   ├── reporting-service/                   # Read-only projection tables, CSV exports
│   ├── platform-service/                    # Settings, feature flags, audit redaction, jobs
│   ├── finance-service/                     # Fee structures, invoices, double-entry GL, refunds
│   └── payroll-service/                     # Staff salaries, gross-to-net engine, disbursements
│
├── libs/                                    # Shared Python Libraries
│   ├── smartedu_contracts/                  # Inter-service event schemas & token signing
│   ├── smartedu_infra/                      # Database sessions, redis clients, base models
│   ├── smartedu_observability/              # OpenTelemetry, structured logging, Prometheus
│   ├── smartedu_perf/                       # Latency profiling & caching helpers
│   └── smartedu_security/                   # Live access middleware, password hashing, HMAC
│
├── infra/                                   # Infrastructure & Deployment Manifests
│   ├── docker-compose.local.yml             # Local Docker Compose (PostgreSQL, RabbitMQ, etc.)
│   ├── gateway/                             # Nginx API Gateway configuration templates & snippets
│   ├── postgres/                            # PostgreSQL 16 initialization scripts
│   ├── rabbitmq/                            # RabbitMQ 4.1 exchange & queue configuration
│   ├── redis/                               # Redis durable & cache configuration
│   ├── minio/                               # MinIO S3 bucket policies & setup scripts
│   └── observability/                       # Prometheus alerting rules, Grafana dashboards, Loki
│
├── scripts/                                 # Operational, Diagnostic & Testing Scripts
│   ├── supervisor.py                        # Unified process supervisor daemon (12 APIs + workers + UI)
│   ├── verify_live_local.py                 # Master 38-case system-wide regression test suite
│   ├── verify_isolated_restore.py           # Disaster recovery isolated DB restore verification
│   ├── package_client_delivery.py           # Clean delivery packager (excludes temp/cache/patches)
│   ├── local_stack.py                       # Local environment orchestrator
│   └── seed_local_demo.py                   # Demo dataset seeder
│
├── tests/                                   # Enterprise Verification & E2E Suites
│   ├── integration/                         # Real Postgres & RabbitMQ integration tests
│   ├── e2e/                                 # Playwright browser automation specs
│   ├── security/                            # Authorization matrix & privilege escalation tests
│   ├── performance/                         # Latency budgets & load smoke benchmarks
│   ├── observability/                       # Telemetry structure & runbook anchor tests
│   └── workflows/                           # Role-based workflow validation schemas
│
├── config/                                  # Environment definitions & shared configs
├── contracts/                               # OpenAPI & Event contract schemas
└── docs/                                    # Technical documentation & sprint records
```

---

# SECTION 2 — SYSTEM SETUP & RUNNING GUIDE

### Step 1: System Requirements & Prerequisites
Ensure the host machine has the following tools installed:
- **Docker Engine / Docker Desktop** (version 24.0+ with Docker Compose v2)
- **Python 3.11 or 3.12**
- **Node.js 20.x LTS** (with npm 10+)
- **PowerShell** (version 7+ recommended; Windows PowerShell 5.1 supported)

### Step 2: Unpack the Archive
```powershell
Expand-Archive -Path SmartEdu_Client_Delivery_Wave17.zip -DestinationPath C:\SmartEdu
Set-Location -Path C:\SmartEdu\smart-education-platform
```

### Step 3: Launch Docker Infrastructure
Start PostgreSQL, RabbitMQ, Redis, MinIO, Mailpit, and the API Gateway containers:
```powershell
docker compose -f infra/docker-compose.local.yml up -d
```
Verify that all 7 containers are healthy:
```powershell
docker compose -f infra/docker-compose.local.yml ps
```

### Step 4: Configure Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Step 5: Install & Build React Frontend
```powershell
Set-Location -Path apps\frontend
npm install
npm run build
Set-Location -Path ..\..
```

### Step 6: Launch All Services & UI with Supervisor
```powershell
python scripts\supervisor.py
```
The supervisor manages all twelve microservice APIs, background event consumers, and the web frontend.

---

# SECTION 3 — ACCESS ENDPOINTS & PORTS

| Component | Port | URL | Description |
| :--- | :--- | :--- | :--- |
| **Frontend Web App** | `5173` | **[http://localhost:5173](http://localhost:5173)** | Complete React 18 / Tailwind web portal |
| **API Gateway** | `18080`| **[http://localhost:18080](http://localhost:18080)** | Central entry point for external API traffic |
| **Identity Service** | `8001` | `http://127.0.0.1:8001/health` | Authentication, JWT, roles |
| **Academic Service** | `8002` | `http://127.0.0.1:8002/health` | Curriculum, catalog, enrollments |
| **Attendance Service** | `8003` | `http://127.0.0.1:8003/health` | Session marking, summaries |
| **Scheduling Service** | `8004` | `http://127.0.0.1:8004/health` | Timetables, recurring classes |
| **Notification Service** | `8005` | `http://127.0.0.1:8005/health` | Announcements, email delivery |
| **Facility Service** | `8006` | `http://127.0.0.1:8006/health` | Campus room reservations |
| **Learning Service** | `8007` | `http://127.0.0.1:8007/health` | Course notes, private S3 files |
| **Assessment Service** | `8008` | `http://127.0.0.1:8008/health` | Quizzes, auto-grading, timers |
| **Reporting Service** | `8009` | `http://127.0.0.1:8009/health` | Analytics, projections, CSV exports |
| **Platform Service** | `8010` | `http://127.0.0.1:8010/health` | Settings, feature flags, audit logs |
| **Finance Service** | `8011` | `http://127.0.0.1:8011/health` | Fee structures, invoices, GL, refunds |
| **Payroll Service** | `8012` | `http://127.0.0.1:8012/health` | Staff payroll, gross-to-net, payouts |
| **Mailpit (Webmail)** | `18025`| **[http://localhost:18025](http://localhost:18025)** | Local email inbox UI |
| **RabbitMQ Management** | `55673`| **[http://localhost:55673](http://localhost:55673)** | Message queue monitoring console |
| **MinIO Console** | `59001`| **[http://localhost:59001](http://localhost:59001)** | Private object storage file browser |

---

# SECTION 4 — TESTING & VERIFICATION GUIDE

### 1. Live Regression Test Suite (38 Cases)
Exercises real PostgreSQL schemas, RabbitMQ events, cookie rotation, GL balance invariance, and maker-checker segregation:
```powershell
python scripts\verify_live_local.py
```
*Expected Result*: `{"PASS": 38, "FAIL": 0}` (Exit code `0`).

### 2. Isolated Disaster Recovery Restoration Verification
Rehearses restoring all 12 database archives into isolated disposable databases, verifying table inventories, row counts, foreign keys, and double-entry trial balance parity:
```powershell
python scripts\verify_isolated_restore.py
```
*Expected Result*: `ALL 12 DATABASES PASS` (Exit code `0`).

### 3. Finance & Payroll Domain Tests
```powershell
pytest -c services/finance-service/pyproject.toml services/finance-service/tests
pytest -c services/payroll-service/pyproject.toml services/payroll-service/tests
```
*Expected Result*: 18 finance tests passed, 16 payroll tests passed.

### 4. Real PostgreSQL & RabbitMQ Integration Tests
```powershell
pytest tests/integration/test_wave17_real_postgres_rabbitmq.py tests/integration/test_architecture_boundaries.py
```
*Expected Result*: 17 passed in ~5s.

### 5. Frontend Unit Tests (Vitest)
```powershell
cd apps\frontend; npm test -- --run; cd ..\..
```
*Expected Result*: 41 passed across 15 test files.

### 6. Browser End-to-End Tests (Playwright)
```powershell
cd tests\e2e; npx playwright test specs\wave17-finance-payroll.spec.ts; cd ..\..
```
*Expected Result*: 7 passed in ~23s.

---

# SECTION 5 — USER MANUAL & STEP-BY-STEP ROLES WALKTHROUGH

### Seeded Demo Accounts

| Role | Email Address | Password | Workspace URL |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@demo.example.edu` | `Demo!UCxagNDHeToFSZXHcdxlRiie7aZ` | `/app/admin` |
| **Faculty / Teacher** | `teacher@demo.example.edu` | `Q7!Oa8xZ24L2aX0dEnj8TuSWGEoDgN-vY8KxEVrnts6cbAaZ` | `/app/teacher` |
| **Student** | `student@demo.example.edu` | `Q7!vEpzlshyGXIddiaOLN7GT73b1cUc71pLVJ1ybXGm5dUaZ` | `/app/student` |

---

### 1. Institutional Administrator Manual (`/app/admin`)

#### A. Academic Curriculum & Student Roster
1. Navigate to **Academic** in the sidebar.
2. Review active Departments (e.g., Computer Science) and Degree Programs.
3. Inspect Courses and Sections. Enrolled students are visible in section rosters. Enrolling a student automatically emits an event that provisions their student fee ledger in the Finance service.

#### B. Institutional Finance & Fee Management
1. Navigate to **Finance** (`/app/admin/finance`).
2. **Fee Structures**: View or edit program fee schedules broken down by Tuition, Laboratory, Library, and Exam funds.
3. **Scholarships**: Review concessions (e.g., 25% Merit Scholarship). When student academic eligibility meets requirements, the discount applies automatically to tuition line items.
4. **General Ledger (GL) & Trial Balance**:
   - Inspect the Chart of Accounts (Cash, Accounts Receivable, Tuition Revenue, Concession Expense).
   - Click **Run Trial Balance** to verify that $\sum \text{Debits} == \sum \text{Credits}$.
5. **Refunds & Maker-Checker Dual Control**:
   - Review pending student refund requests.
   - **Maker-Checker Rule**: The officer who logs a refund request cannot approve it. A second distinct administrator must approve or reject it.

#### C. Institutional Payroll & Human Resources
1. Navigate to **Payroll** (`/app/admin/payroll`).
2. **Employee Profiles**: Review faculty designations, base salaries, and registered bank accounts.
3. **Monthly Payroll Runs**:
   - Select an active period and initiate a payroll run.
   - The gross-to-net engine calculates base salary, medical/housing allowances, and tax deductions.
4. **Maker-Checker Run Approval**:
   - The creator of the run cannot approve it. A separate checker reviews calculations and approves the payout batch.
5. **Simulated Payouts & Reconciliation**:
   - Execute batch disbursements to the simulated 1Link banking network.
   - If an uncertain banking response occurs, run **Batch Reconciliation** to confirm the final outcome without duplicate financial changes.

#### D. Governance, Audit Trails & Platform Operations
1. Navigate to **Platform & Governance** (`/app/admin/platform`).
2. Search security audit records by actor, date range, or request ID. Tokens and passwords are automatically redacted.
3. Manage versioned feature flags and trigger dry-run data imports.

---

### 2. Faculty / Teacher Manual (`/app/teacher`)

1. **Teaching Timetable**:
   - View your weekly teaching schedule with room assignments and lecture times (`/app/teacher/timetable`).
2. **Student Attendance Marking**:
   - Open **Attendance** (`/app/teacher/attendance`).
   - Select your section and date to open a session.
   - Use the bulk-mark interface to set student attendance (`PRESENT`, `ABSENT`, `EXCUSED`).
   - Finalize the session to lock records.
3. **Online Quizzes & Assessments**:
   - Navigate to **Assessments** (`/app/teacher/assessments`).
   - Create quizzes with multiple-choice questions and set time limits.
   - Review auto-graded submissions and score distributions.
4. **Personal Payslips**:
   - Open **Payroll** (`/app/teacher/payroll`) to inspect your monthly salary breakdown (Gross, Deductions, Net Pay). Student access to teacher payslips is strictly denied.

---

### 3. Student Manual (`/app/student`)

1. **Academic Dashboard & Timetable**:
   - View enrolled courses, upcoming lectures, and class locations (`/app/student/timetable`).
2. **Learning Materials**:
   - Access lecture slides, syllabus documents, and supplementary files uploaded by faculty (`/app/student/learning`).
3. **Taking Quizzes**:
   - Open **Assessments** (`/app/student/assessments`) to start an assigned quiz.
   - Answer questions before the countdown timer expires and submit your attempt.
4. **Student Fee Portal & Payment Checkout**:
   - Navigate to **Finance** (`/app/student/finance`).
   - View tuition invoices, due dates, installment breakdown, and applied merit scholarships.
   - Click **Pay Now** to launch the payment modal.
   - Select your payment gateway (**JazzCash**, **EasyPaisa**, or **Bank Transfer**).
   - Click **Confirm Payment** to trigger simulated instant settlement.
   - Download the official payment receipt; the invoice updates to `PAID` with zero balance.

---

# SECTION 6 — SAFETY & SANDBOX NOTICE

> [!IMPORTANT]
> **Simulated Financial Rails**: All payment gateways (JazzCash, EasyPaisa, Stripe) and bank payouts (1Link) run on deterministic simulation adapters. No real credit card or bank account will ever be charged.
> 
> **Production Hardening Prerequisite**: Before general production release, external TLS termination, multi-AZ PostgreSQL failover, and production payment provider merchant agreements must be configured.

