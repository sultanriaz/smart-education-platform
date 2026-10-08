# Integration progress

Updated 2026-10-08 (Asia/Karachi). Current milestone: local integration and demonstration delivery; external acceptance gates remain pending.

- Original HEAD: `8a4cc6a` on `master`; no modified tracked files. 25 untracked sprint archives preserved.
- Integration branch: `integration/2026-10-08`.
- Recovery checkpoint: `.integration/pre-integration.bundle` (all original Git refs).
- Available packages: Sprints 4–28 in repository root. `sprint-zips` and packages 1–3 unavailable.
- Existing independent services: Identity, Academic, Attendance. Frontend: Vite starter.
- Docker client installed; engine unavailable at first inspection.
- User confirmed no final approved SRS exists. Proceed using directive, sprint instructions, implemented contracts/business rules, then quality targets. Draft as-built requirements are maintained under `docs/requirements`.

Completed: staged and chronologically reconciled all available archives; integrated ten APIs, gateway, thirteen libraries, and three role workspaces; wired security/contracts/telemetry; repaired refresh cookies/recovery, Academic adapters, Learning migrations, authenticated Redis and gateway runtime; connected durable publishers and Notification/Reporting/Platform consumers; implemented premium responsive UI and route splitting; applied ten service migrations in isolated PostgreSQL; seeded labelled demo workflows through service APIs.

Local frontend: `http://localhost:5173`. Gateway: `http://localhost:18080` (8080 is reserved by Windows). Generated secrets/fixtures/logs remain ignored under `.integration/runtime`; unrelated Docker projects and original `.env` files are preserved.

Verified local evidence: 648 backend/library/gateway/system tests passed with 98 explicit skips; 40 frontend tests passed; ten built service containers passed owned migration readiness and authenticated APIs; 31 live integration cases passed, including a real one-minute worker-driven assessment expiry with late-edit rejection. All 18 browser tests passed. Frontend lint/build and Python service/library lint passed. Real browser navigation, save/resume, expiry, role isolation, private object storage, encrypted recovery delivery and durable events are recorded in the [final delivery report](FINAL_DELIVERY_REPORT.md). The page review covers 31 records and 140 width checks with zero recorded axe violations/overflow/page errors.

Performance remains qualified: the 20-user/120s CSV records 799 requests with zero failures and P95 65 ms. The latest 500-user/600s diagnostic failed: 90,982 requests, 73,224 failures (73,014 HTTP 429 and 210 HTTP 503). One generator IP/three identities exceeded preserved security throttles, and image builds overlapped part of the run. The unreachable Docker Desktop IPv6 route was fixed, but the latest timeouts and rejected requests remain failures. PostgreSQL owner query plans were measured against small demo tables; this does not establish production capacity.

Checkpoint `6a17059` contains the integrated source. Final follow-up changes include tested dependency constraints, Linux image verification, line-ending normalization, local IPv4 transport, assessment expiry, real query-plan evidence and completed draft requirements/run instructions. Original ZIPs, recovery bundle and early failure logs remain available. No remote push or production release was performed.

Skipped tests are never counted as passes. Image CVE/signing, hosted CI, Kubernetes/staging/production deployment, institutional UAT/signoff, sustained availability and production recovery remain unverified external gates. Missing approved SRS documentation did not block implementation.
