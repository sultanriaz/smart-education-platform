# Final integration delivery report

Updated 2026-10-08. Local engineering evidence; not institutional acceptance or a production release.

## A. Integration

Integrated 25 supplied packages (Sprints 4–28); retained Sprints 1–3 from original Git HEAD `8a4cc6a`. No packages 1–3 or `sprint-zips` directory were available. Validated 1838 archive file entries; 1833 provenance actions are retained under ignored `.integration/merge-manifest.json`. The local branch is `integration/2026-10-08`; recovery bundle and original ZIPs remain available.

Ten independent services, thirteen shared libraries, gateway, three role workspaces, migrations, infrastructure and operational catalogs are integrated. [Architecture](SYSTEM_ARCHITECTURE.md), [inventory](SPRINT_INVENTORY.md), [conflicts](MERGE_DECISIONS.md), [limits](KNOWN_LIMITATIONS.md).

| Sprint | Final status |
|---|---|
| 1 | Identity baseline retained; suite and live authentication verified |
| 2 | Academic baseline retained; suite and owner contracts verified |
| 3 | Attendance baseline retained; suite and live finalization/summary verified |
| 4 | Scheduling integrated; real recurring timetable verified |
| 5 | Notification integrated; real announcement/SMTP/event delivery verified |
| 6 | Facility integrated; approval, conflict and isolation verified |
| 7 | Learning integrated; real notes and private S3 round trip verified |
| 8 | Assessment integrated; real answers/grading, saved progress and timed expiry verified |
| 9 | Reporting integrated; real broker projection and CSV verified |
| 10 | Platform integrated; durable health/reindex/Academic export jobs verified |
| 11 | Gateway integrated; real routing/CORS, private routes and non-root startup verified |
| 12 | Frontend shell integrated and modernized |
| 13 | Student workspace integrated; routes/browser workflow verified |
| 14 | Teacher workspace integrated; routes and authorization verified |
| 15 | Admin workspace integrated; routes and authorization verified |
| 16 | Contracts/resilience integrated; suites and real Redis idempotency verified |
| 17 | Owned migrations, RabbitMQ, Redis and private storage integrated and started |
| 18 | Security integration, recovery/cookies/uploads verified within stated limits |
| 19 | QA libraries/suites integrated and executed; conditional skips retained |
| 20 | Performance tooling integrated; real local measurements below |
| 21 | Telemetry wiring and suites verified; external collector pipelines NOT RUN |
| 22 | CI/CD catalogs and local validation pass; hosted workflows NOT RUN |
| 23 | Deployment topology/tooling integrated; actual cluster deployment NOT RUN |
| 24 | Staging tooling/suites integrated; staging execution NOT RUN |
| 25 | UAT tooling/suites integrated; institutional UAT/signoff NOT RUN |
| 26 | Readiness tooling/suites integrated; real production gates NOT RUN |
| 27 | Production release tooling integrated; production deployment NOT RUN |
| 28 | Stabilization tooling integrated; production observation/drills NOT RUN |

Conflicts resolved: chronological schema/runtime extensions; Student read and Teacher authoring contracts; all role routes retained when recovery routes were added; stable idempotency and authenticated downloads retained with cookie sessions; independent owned migrations/event stores; root-context Docker library paths; local host routing/CORS and protected infrastructure configuration. No old-SRS omissions caused feature deletion.

## B. Functional results

| Component | Local result / evidence |
|---|---|
| academic-service | PASS: 85 passed, 5 skipped, 1 warning in 7.76s |
| assessment-service | PASS: 19 passed, 1 skipped in 1.78s |
| attendance-service | PASS: 99 passed, 10 skipped, 1 warning in 4.50s |
| facility-service | PASS: 35 passed, 1 skipped, 2 warnings in 2.02s |
| identity-service | PASS: 47 passed, 2 skipped, 1 warning in 4.39s |
| learning-service | PASS: 35 passed, 1 skipped, 2 warnings in 1.13s |
| notification-service | PASS: 37 passed, 1 skipped, 2 warnings in 1.70s |
| platform-service | PASS: 23 passed, 1 skipped, 1 warning in 1.94s |
| reporting-service | PASS: 12 passed, 1 skipped in 2.04s |
| scheduling-service | PASS: 27 passed, 1 skipped, 2 warnings in 1.32s |
| API Gateway | Built/running Nginx; namespace routing, CORS and public internal-route rejection verified |
| Student frontend | Actual attendance/timetable/resources/assessment/booking data; saved assessment resume/submission verified |
| Teacher frontend | Actual sections/attendance/timetable/resources/assessment/announcements/facilities pages; backend ownership checks |
| Admin frontend | Actual user/academic/scheduling/facility/notification/reporting/platform pages |

Representative full-system checks:

| Live case | Result | Evidence |
|---|---|---|
| identity: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| academic: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| attendance: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| scheduling: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| notification: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| facility: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| learning: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| assessment: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| reporting: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| platform: health and owned migration readiness | PASS | Both endpoints returned 200 against the migrated PostgreSQL database |
| student: real login and cookie security | PASS | Access token in memory; rotating refresh credential is HttpOnly and SameSite=Strict |
| teacher: real login and cookie security | PASS | Access token in memory; rotating refresh credential is HttpOnly and SameSite=Strict |
| admin: real login and cookie security | PASS | Access token in memory; rotating refresh credential is HttpOnly and SameSite=Strict |
| Gateway: cross-service CORS preflights and private route blocking | PASS | Nine namespaces support approved preflight; internal routes and untrusted CORS remain unavailable |
| Academic: enrollment, roster and teacher assignment contracts | PASS | Real owner relationships work; Student cannot modify the academic catalog |
| Attendance: finalized records, correct summary and write isolation | PASS | Five final records produce 80%; finalized writes and Student writes are rejected |
| Attendance: real owned bulk mark within two seconds | PASS | Real PostgreSQL bulk mark and owner read-back succeeded in 0.063s; disposable session remains OPEN |
| Scheduling: recurring occurrences visible to enrolled Student | PASS | 2 real occurrences returned |
| Learning: PostgreSQL resources, notes and recommendations | PASS | Versioned notes and owner-enforced recommendations resolve through signed Academic contracts |
| Learning: private S3 upload/download, validation and ownership | PASS | Real private object round-trip/checksum; anonymous access and cross-service bucket access denied; MIME validation and Student upload denial verified |
| Assessment: safe questions, persisted answers and automatic grading | PASS | Committed answer graded 5/5 and 100%; answer keys absent from Student read response |
| Assessment: real timer expires saved answers without Student activity | PASS | Real 60-second timer finalized saved answers through the owned worker; Teacher observed 100% before any Student read; late edits rejected and repeated submit preserved the result |
| Facility: approval, overlap rejection and requester isolation | PASS | Approved booking blocks overlaps; unrelated requester receives 403 |
| Notification: actual announcement delivery within five seconds | PASS | Announcement persisted and reached Student in 0.906s; mark-read succeeded |
| Platform: request idempotency and ticket isolation | PASS | Retry returns the same ticket; conflicting body and unrelated requester are rejected |
| Platform: durable health, reindex and signed owner export jobs | PASS | All ten services ready; durable health/reindex/export jobs completed via owner contracts |
| Reporting: RabbitMQ grade projection and actual CSV export | PASS | Committed grade arrived through broker/inbox and appears in Admin-only CSV |
| Identity: real SMTP recovery, single use and refresh revocation | PASS | Encrypted outbox delivered a real Mailpit email; reset is single-use and revokes prior refresh session |
| Academic: signed owner import rollback is atomic | PASS | Duplicate batch rejected and its earlier valid row rolled back in Academic's owned transaction |
| Security: ten PostgreSQL owner roles reject foreign data access | PASS | All 10 service roles denied access to another owner's data by PostgreSQL permissions |
| Security: scoped internal authentication and gateway token integrity | PASS | Signed service scopes are enforced; anonymous requests cannot impersonate users or services |

## C. UI/UX

Replaced the Vite starter/sprint shell with shared light/dark violet, navy and charcoal tokens, polished cards, real charts, personalized dashboards, role navigation, profile/logout, notification badges, page finder and keyboard shortcuts. Lazy pages provide loading/error/empty states. Touch targets, responsive tables and navigation support 320/375/768/1024/1440 widths. Motion uses brief transform/opacity transitions and honors reduced-motion preferences.

Browser page review: 31 records (role pages plus dark dashboard checks); 140 width checks. Findings remain in `artifacts/browser/review.json`. Axe targets WCAG 2 A/AA and 2.1 AA; automated checks are not human accessibility acceptance.

Local screenshots: [Student desktop](../../artifacts/browser/student-desktop.png), [Student dark](../../artifacts/browser/student-dark.png), [Student mobile](../../artifacts/browser/student-mobile.png), [Teacher desktop](../../artifacts/browser/teacher-desktop.png), [Teacher mobile](../../artifacts/browser/teacher-mobile.png), [Admin desktop](../../artifacts/browser/admin-desktop.png), [Admin dark](../../artifacts/browser/admin-dark.png). Before screenshots were not captured; original source is retained for comparison.

## D. Debugging and optimization

| Problem / root cause | Repair and measured boundary |
|---|---|
| PostgreSQL DISTINCT over JSON failed although SQLite suites passed | Learning uses a unique target-ID subquery; real Student catalog now succeeds |
| Attendance totals wrapper and obsolete routes produced incorrect UI/404s | Actual totals mapped to 80%; Teacher sessions/records and Admin assignments use owner contracts |
| Login cookies/recovery adapters were not connected to actual accounts | Owned token/account/outbox adapters, threadpool Argon2/DB calls, strict HttpOnly refresh and real encrypted SMTP delivery |
| Platform multiline application constructor missed contract middleware | Actual installation and regression test; real retry returns one ticket and body conflict returns 409 |
| Archived outbox/worker extensions were present but not executing | Owned durable publishers/consumers, retries/quarantine, real projections and jobs |
| Graded attempt GET omitted results; reload consumed attempts | Safe persisted grade/answer DTO, own active-attempt contract, browser resume and locked answer/submit writes |
| Cross-question choice input was accepted | Owner question-choice validation rejects it before persistence |
| Quiz duration was displayed without enforcement | Persisted earlier timer/deadline, indexed bounded expiry worker, locked late-edit rejection, server-clock countdown and idempotent submission; blank written responses remain gradeable |
| Snapshot filters were silently ignored | Scalar column equality filters applied; unsupported input returns a domain error |
| Registry could target arbitrary origins | Explicit host allowlist and origin/path validation; custom deployment hosts require `SERVICE_REGISTRY_ALLOWED_HOSTS` |
| Repeated HTTP/TLS setup dominated local service calls | Bounded per-origin clients reuse connections; per-request authorization and rejected cookie persistence are regression tested |
| Large eager frontend bundle | Initial 605.69 KB / 163.4 KB gzip main bundle became 331.91 KB / 103.24 KB gzip plus lazy chunks; CSS 39.15 KB / 8.97 KB gzip |
| Mobile overflow and inaccessible Admin role selector | Grid/min-width constraints, truncation and labels; complete page width/axe review |
| Gateway non-root PID path denied startup | `/tmp/nginx.pid`, writable template/cache directories and verified non-root startup |
| Docker Desktop's native-host alias selected unreachable IPv6 under load | Explicit local-only host-gateway IPv4 selection; latest diagnostic has zero network-unreachable errors; remaining throttles/timeouts remain failures |
| Container dependency download/resolution failed | Shared tested-version constraints and host-downloaded Linux wheels; SHA-256 checks preserved; all ten service images built and their authenticated APIs verified |

Database pools, connection/read/statement timeouts and request/upload limits are bounded. Authorization relationships are never cached across callers. Publishing holds an owned row lock through bounded broker confirmation; consumers deduplicate in their own transactions. These controls are not evidence of production availability or DR acceptance.

PostgreSQL `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` was executed through each owner's local credentials for finalized attendance aggregation, unique learning-resource target IDs and bounded expired-attempt selection. Full plans are in `artifacts/performance/query-plans.json`. These small labelled tables do not justify speculative indexes or certify production query scalability.

| Measured owner query | Planning | Execution |
|---|---:|---:|
| attendance: finalized_student_summary | 1.911 ms | 0.144 ms |
| learning: unique_section_resource_ids | 0.739 ms | 0.054 ms |
| assessment: bounded_expired_attempts | 0.870 ms | 0.065 ms |

## E. Test evidence

Latest isolated totals: **648 passed, 0 failed, 98 skipped** across 25 service/library/gateway/system suites. Skips include explicitly configured PostgreSQL/concurrency and external live-environment cases; they remain SKIPPED even when a separate representative local test passes. See [exact suite results](TEST_RESULTS.md).

| Check | Actual result |
|---|---|
| Backend/shared libraries/contracts/gateway/system | Recorded suite results above; separate-process execution avoids unrelated `app` package collisions |
| Frontend unit tests | PASS: 40 tests across 15 files, including deadline/clock-skew checks |
| TypeScript/Vite build | PASS; production preview exercised |
| Frontend lint | PASS, zero warnings |
| Python service/library lint | PASS after fixes; actual command in runbook |
| Playwright latest | 18 expected/passed; 0 unexpected/failed; 0 skipped; 0 flaky |
| Live integration | 31 PASS, 0 FAIL |
| Security checks | Generated-secret scan, non-root Dockerfile audit, ownership/cookie/recovery/internal-scope/storage checks; image CVE scan NOT RUN |
| Dependencies | pip check PASS; production npm audit zero reported vulnerabilities |
| Docker startup | PostgreSQL, two Redis, RabbitMQ, Mailpit, MinIO and Nginx PASS; owned MinIO policies/bootstrap PASS |
| Service Docker images | 10 PASS, 0 FAIL: built images started as non-root, passed owned migration readiness and real authenticated API requests |
| 20-user smoke, 120 seconds | 799 requests; 0 failures; P95 65 ms; P99 980 ms; mean 49.61 ms |
| 500-user diagnostic, 600 seconds | FAIL: 90982 requests; 73224 failures; P95 250 ms; P99 550 ms; mean 72.02 ms; HTTP 429: 73014; HTTP 503: 210 |
| Staging/production/UAT/DR/99% availability | NOT RUN or unresolved real acceptance; local tooling tests do not substitute |

The earlier load run was interrupted by gateway hardening and is retained under `artifacts/performance/interrupted-500`; it is not acceptance evidence. Early failing test/build runs and logs remain under `.integration/runtime`. The latest 500-user diagnostic shares one IP/three identities with security throttles enabled; local image builds overlapped part of the run. Its 429 rejections and 503 upstream timeouts are failures. Low response percentiles dominated by rejected requests do not establish successful interaction latency, an approved workload or production capacity. Exact environment caveats are retained in `artifacts/performance/srs-500-environment.json`.

The initial Docker download hash mismatch was identified for the cryptography Linux wheel. The verified host download and cache resolved the build path without accepting the mismatched artifact. Image CVE scans, signing and real cluster deployment remain NOT RUN. `artifacts/verification/container-results.json` records each of the ten actual container/API outcomes.

## F. Exact Windows run instructions

See the numbered PowerShell commands in [README](../../README.md). `scripts/local.ps1` provides Configure, Infrastructure, Migrate, Services, Seed, Frontend, Test and Stop actions. APIs start before API-based seeding. Local application: `http://localhost:5173`; gateway: `http://localhost:18080`; real demo mail: `http://localhost:18025`. Credentials are generated in ignored `.integration/runtime/secrets.json`; no production password is provided or committed.

Stop preserves service databases, Docker volumes, sprint inputs and unrelated projects. Local frontend preview is intended for demonstration; external production deployment follows the separately verifiable topology/release gates.

## G. FYP readiness

The native local demonstration has ten migrated owner APIs, three modern role workspaces, real linked demo data, durable background workers, recovery email and private file storage. Demonstrate Student attendance/timetable/learning/assessment progress, Teacher announcements, booking approval/conflicts and Admin reporting/health/jobs. Automated evidence establishes the specific workflows above.

Full institutional acceptance and production readiness are **not complete**. The 500-user target must be evaluated with its actual rejection rate and an approved distributed workload; image CVE scans/signing, hosted CI, cluster deployment, production secrets/DNS/TLS, staging/UAT, sustained availability and recovery objectives remain external gates. [Known limits and proposed improvements](KNOWN_LIMITATIONS.md) explicitly separate present implementation from future work.
