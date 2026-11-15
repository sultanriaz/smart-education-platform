# SmartEdu Platform — Client Delivery & Operations Guide
## Wave 17 Enterprise Release | Twelve Microservices | React Frontend | API Gateway

---

## 1. System Overview & Architecture

The **Smart Education Platform (SmartEdu)** is an enterprise educational and institutional management platform built on a decoupled, microservices-based architecture.

```text
+-----------------------------------------------------------------------------------+
|                           REACT / TYPESCRIPT WEB FRONTEND                         |
|                                (Vite SPA on Port 5173)                            |
+-----------------------------------------------------------------------------------+
                                          |
                                          | (Reverse Proxy & Security Rate-Limiting)
                                          v
+-----------------------------------------------------------------------------------+
|                             NGINX API GATEWAY (Port 18080)                         |
+-----------------------------------------------------------------------------------+
       |            |             |            |            |             |
       v            v             v            v            v             v
 [Identity]    [Academic]   [Attendance]  [Scheduling] [Notification] [Facility]
   (:8001)       (:8002)       (:8003)       (:8004)       (:8005)      (:8006)
       |            |             |            |            |             |
       v            v             v            v            v             v
  [Learning]  [Assessment]   [Reporting]   [Platform]    [Finance]     [Payroll]
   (:8007)       (:8008)       (:8009)       (:8010)       (:8011)      (:8012)
+-----------------------------------------------------------------------------------+
|                               SHARED INFRASTRUCTURE                               |
| - PostgreSQL 16 (12 Isolated Schemas & Service Roles on Port 15432)               |
| - RabbitMQ 4.1 (Event Bus & Asynchronous Worker Queues on Port 55672)              |
| - Redis 7.4 (Durable Idempotency on 56380 & Cache on 56379)                       |
| - MinIO S3 (Private Educational Object Storage on Port 59000/59001)                |
| - Mailpit (Local SMTP Server & Webmail on Port 11025/18025)                       |
+-----------------------------------------------------------------------------------+
```

### Core Architecture Principles
1. **Database Schema Isolation**: Each microservice owns its private PostgreSQL database and dedicated credentials (`<name>_svc`). Cross-database foreign queries are rejected at the PostgreSQL permission layer.
2. **Cryptographic Inter-Service Authentication**: Microservices communicate asynchronously via RabbitMQ events and synchronously via Ed25519-signed internal JWT tokens with scoped audience parameters.
3. **Double-Entry General Ledger**: The Finance domain uses an immutable double-entry accounting engine (`Debits == Credits`) for all invoice billings, concessions, payments, and refunds.
4. **Segregation of Duties (Maker-Checker)**: High-risk financial operations (student refunds, payroll run approvals) prohibit creator self-approval and enforce distinct dual-control authorization.
5. **Simulated External Transactions**: All payment gateway callbacks (JazzCash, EasyPaisa, Stripe) and bank disbursements (1Link) run deterministic mock adapters. Real financial transfers are disabled for sandbox safety.

---

## 2. Prerequisites & Environment Requirements

Before running the platform, ensure the following software is installed on the host system:

| Dependency | Minimum Version | Recommended Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10/11, Ubuntu 22.04 LTS, or macOS 13+ | Windows 11 / Linux | Host OS |
| **Docker Desktop / Engine** | 24.0+ | Latest with Compose v2 | Infrastructure containers |
| **Python** | 3.11 or 3.12 | 3.12.x | Microservice backends |
| **Node.js** | 20.x LTS | 20.18+ (with npm 10+) | React frontend build and runtime |
| **PowerShell** | 7.x (or Windows PowerShell 5.1) | PowerShell 7+ | Automation scripts |

---

## 3. Quickstart: Installation & Startup Guide

### Step 1: Extract the Delivery Package
Extract the delivery archive to your desired workspace directory:
```powershell
Expand-Archive -Path SmartEdu_Client_Delivery_Wave17.zip -DestinationPath C:\SmartEdu
Set-Location -Path C:\SmartEdu
```

### Step 2: Infrastructure (Optional / General Standalone Mode)
- **Without Docker (Default Standalone Mode)**: No Docker installation or setup is required. The platform includes a native Python API Gateway and runs directly on host Python and Node.js. Simply skip to Step 3.
- **With Docker (Containerized Supporting Infrastructure)**: If Docker Engine is available, you can optionally start the local databases and queue containers:
  ```powershell
  docker compose -f docker-compose.local.yml up -d
  ```

### Step 3: Set Up Python Virtual Environment
Initialize Python dependencies and install shared libraries in editable mode:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Step 4: Install Frontend Dependencies
```powershell
Set-Location -Path apps\frontend
npm install
npm run build
Set-Location -Path ..\..
```

### Step 5: Start the Platform (Unified Single Running Point)
Start all 12 microservice APIs, RabbitMQ background workers, and the frontend server using the unified root runner:
```powershell
python run.py
```
> **Tip:** You can also check system status at any time with `python run.py --status`, view credentials with `python run.py --credentials`, or stop all running services with `python run.py --stop`.

Once started, the following services will be available:
- **Frontend Web Portal**: [http://localhost:5173](http://localhost:5173)
- **API Gateway**: [http://localhost:18080](http://localhost:18080)
- **Mailpit Webmail**: [http://localhost:18025](http://localhost:18025)
- **RabbitMQ Management**: [http://localhost:55673](http://localhost:55673) (user: `smartedu`)
- **MinIO S3 Console**: [http://localhost:59001](http://localhost:59001)

---

## 4. Verification & Testing Guide

The delivery package includes automated testing suites to verify the platform end-to-end:

### A. Live System Regression Suite (38 Test Cases)
Verifies all 12 services, cookie security, PostgreSQL role isolation, RabbitMQ event processing, double-entry accounting balances, and maker-checker segregation:
```powershell
python scripts\verify_live_local.py
```
*Expected Output*: `{"PASS": 38, "FAIL": 0}` with exit code `0`.

### B. Isolated Disaster Recovery Restoration Verification
Verifies that all 12 database checkpoint archives restore cleanly into isolated disposable databases and maintain cryptographic integrity:
```powershell
python scripts\verify_isolated_restore.py
```
*Expected Output*: `ALL 12 DATABASES PASS`.

### C. Finance & Payroll Domain Test Suites
Runs backend unit tests covering fee calculation, installment plans, overdue penalty schedules, gross-to-net payroll, maker-checker authorization, and retry safety:
```powershell
pytest -c services/finance-service/pyproject.toml services/finance-service/tests
pytest -c services/payroll-service/pyproject.toml services/payroll-service/tests
```

### D. Real PostgreSQL & RabbitMQ Integration Tests
Tests real transactional enrollment-to-invoice generation, inbox deduplication, and worker crash recovery against live containers:
```powershell
pytest tests/integration/test_wave17_real_postgres_rabbitmq.py tests/integration/test_architecture_boundaries.py
```

### E. Frontend Unit & Contract Tests
Runs Vitest unit tests verifying state stores, normalizers, and API contracts:
```powershell
Set-Location -Path apps\frontend
npm test -- --run
Set-Location -Path ..\..
```
*Expected Output*: `15 passed (15 test files), 41 passed (41 tests)`.

### F. Browser End-to-End Tests (Playwright)
Runs browser automation covering student fee checkout, admin maker-checker queues, simulated payout failure/recovery, and general ledger trial balance inspection:
```powershell
Set-Location -Path tests\e2e
npx playwright test specs\wave17-finance-payroll.spec.ts
Set-Location -Path ..\..
```

---

## 5. Cloud Deployment to Vercel

The web application is pre-configured for instant deployment to Vercel:
- Root [`vercel.json`](vercel.json) and [`package.json`](package.json) handle automatic Vite framework detection, dependency installation, and production asset caching.
- Dynamic SPA route rewrites ensure deep links and page refreshes work cleanly.
- See [`VERCEL_DEPLOYMENT_GUIDE.md`](VERCEL_DEPLOYMENT_GUIDE.md) for step-by-step instructions.

```bash
npx vercel --prod
```

---

## 6. Production Deployment Notes & Safety Notice

1. **Simulated Financial Transactions**: The platform currently operates in a development and sandbox profile. Financial payment callbacks and bank disbursements run in simulated mode and will never interact with real banking networks.
2. **Production Prerequisites**: Before deploying to a live production environment:
   - Configure external TLS termination at the load balancer / reverse proxy.
   - Provision production PostgreSQL clusters with automated WAL archiving and multi-AZ failover.
   - Replace local secrets in `.env` with a secure key management system (e.g., HashiCorp Vault, AWS Secrets Manager).
   - Enter institutional merchant agreements with JazzCash, EasyPaisa, or 1Link for real payment rails.

