# Draft requirements traceability

Updated 2026-10-08. Implementation and successful verification remain distinct.

| Requirements | Implementation | Evidence sources |
|---|---|---|
| FR-01; NFR-05/06 | Identity, shared security/contracts, frontend auth/client | Identity/security/contract suites; browser auth/role/storage; recovery SMTP checks |
| FR-02 | Academic models/services/routes/relationship adapter | Academic suite; API-seeded linked demo records |
| FR-03; NFR-03 | Attendance domain/routes/outbox | Attendance suite; live marks/finalization/correction/timing |
| FR-04 | Scheduling and Academic adapter | Scheduling suite; timetable/conflict workflow |
| FR-05; NFR-04/08 | Notification, owned relay, recipient adapters | Notification/relay suites; real RabbitMQ/SMTP/duplicate/timing |
| FR-06 | Facility | Facility suite; booking/approval/conflict |
| FR-07; NFR-05 | Learning/upload/private storage | Learning/upload suite; storage authorization checks |
| FR-08 | Assessment authoring/student/teacher/grading | Assessment suite; live attempt/result |
| FR-09 | Reporting event worker/projector | Reporting suite; real projections/CSV |
| FR-10 | Platform worker/services/routes | Platform suite; support/settings/health/jobs/search |
| FR-11; NFR-01/10/11 | Frontend shell/pages/premium CSS | Build/lint/unit; browser routes/widths/axe/screenshots |
| FR-12; NFR-02/07/09/12 | Infrastructure/deploy/shared libraries/scripts/catalogs | Gateway/system/library suites; local migrations/load; external acceptance pending |

Executed records: [test results](../integration/TEST_RESULTS.md). Provenance: [sprint inventory](../integration/SPRINT_INVENTORY.md), [merge decisions](../integration/MERGE_DECISIONS.md). Full artifacts are retained under ignored `artifacts/`. A skipped or unexecuted test is not successful verification.

Live result mapping: FR-01 recovery/login/cookie cases; FR-02 Academic relationships; FR-03 Attendance; FR-04 Scheduling; FR-05 Notification; FR-06 Facility; FR-07 Learning/S3; FR-08 Assessment; FR-09 Reporting; FR-10 Platform/idempotency/jobs; FR-12 ten readiness cases and Gateway. Exact assertions are in `scripts/verify_live_local.py`; recorded results are `artifacts/integration/live-results.json`. FR-11/NFR-10/11 map to `apps/frontend/scripts/review-complete.cjs` and `artifacts/browser/review.json`. FR-08 resume and NFR-06 inactivity map to named Playwright specs. NFR-01/02 map to Locust CSV/environment records; 500-user rejections do not constitute passing acceptance. [Full report](../integration/FINAL_DELIVERY_REPORT.md) records latest counts and unresolved external gates.
