Integrate Sprint 19 Testing Maturity & Full-System QA into the current Smart
Education Platform.

FIRST inspect the actual merged Sprints 1–18 and inventory every existing test.
Do not delete strong existing tests merely to standardize layout.

The objective is to prove distributed correctness, authorization, migrations,
concurrency, event reliability, and the three role workflows.

1. Shared testkit

   Integrate:
   `libs/python/smartedu_testkit`

   Use it where it reduces duplication, but do not make every service test
   depend on a giant shared fixture module.

   Keep the testkit domain-neutral: no service ORM models.

2. Inventory existing tests

   Produce a table for all ten services with:
   - unit tests
   - PostgreSQL integration tests
   - concurrency tests
   - auth/RBAC tests
   - dependency failure tests
   - migration tests
   - event/outbox/inbox tests
   - current pass count
   - current coverage if available

3. Reconcile SERVICE_TEST_SCENARIOS.yaml

   For each listed critical scenario:
   - point to an existing strong test, or
   - add a real test in the owning service.

   Do not mark a scenario covered by a smoke test if it requires transaction,
   concurrency, or authorization proof.

4. Identity

   Ensure coverage includes Sprints 1, 16, and 18:
   - registration
   - duplicate email
   - Argon2 password hashing
   - login success/failure
   - account lockout
   - refresh rotation
   - rotated-token replay rejection
   - logout revocation
   - JWKS
   - password reset expiry/single use/session revocation
   - email verification expiry/single use
   - HttpOnly refresh cookie
   - missing/untrusted Origin rejection
   - Admin RBAC

5. Academic

   Preserve/expand real PostgreSQL tests:
   - final seat race
   - duplicate enrollment
   - course/section uniqueness
   - Teacher assignment authorization
   - roster derivation
   - transaction rollback

6. Attendance

   Add/verify:
   - Teacher assignment authorization
   - Student enrollment validation
   - bulk atomicity
   - session lifecycle immutability
   - correction audit
   - low-attendance threshold
   - PostgreSQL duplicate/finalize races
   - Academic dependency failure -> 503/fail closed

7. Scheduling

   Add/verify PostgreSQL concurrency for:
   - room conflict
   - Teacher conflict
   - section conflict
   - adjacent slots allowed
   - recurrence
   - cancel/reschedule override
   - Academic dependency failure

8. Notification

   Add/verify:
   - read/unread/archive
   - preference/muting
   - section/role target authorization
   - inbox event dedup
   - retry/delivery audit
   - RabbitMQ retry/DLQ integration
   - Sprint 18 encrypted security-event delivery
   - no plaintext security token persistence/logging

9. Facility

   Add/verify:
   - overlap rejection
   - adjacent slot success
   - PostgreSQL double-booking race
   - approval/rejection/cancel
   - external Scheduling reservation
   - outbox publish semantics

10. Learning

   Add/verify:
   - Teacher/Admin authoring
   - Student enrollment authorization
   - publish/archive/version lifecycle
   - private object storage
   - file size/type/magic checks
   - unsafe filename/path rejection
   - malware scan behavior when required
   - Academic dependency outage
   - S3/MinIO permission denial tests

11. Assessment

   Replace the Sprint 8 PostgreSQL placeholder concurrency test with a real test.

   Required:
   - question validation
   - empty quiz publish rejection
   - Teacher section/course ownership
   - assignment window
   - attempt limit
   - true PostgreSQL concurrent attempt-limit race
   - answer/submit ownership
   - post-submit immutability
   - objective auto-grading
   - manual grade audit
   - grader assignment authorization
   - Student answer-key protection
   - no IN_PROGRESS peer-answer exposure
   - Academic dependency outage

12. Reporting

   Add/verify:
   - duplicate event id
   - out-of-order/late events
   - projection calculations
   - UTC/date filters
   - CSV export
   - role authorization
   - rebuild/backfill behavior
   - RabbitMQ redelivery/restart safety

13. Platform

   Add/verify:
   - audit ingestion
   - event dedup
   - job lifecycle
   - import/export safety
   - admin authorization
   - service health registry/dependency behavior

14. Architecture tests

   Integrate central architecture tests.

   They must enforce:
   - no cross-service ORM/repository imports
   - no frontend direct :8001-:8010 calls
   - one Alembic history per service
   - no root monolithic Alembic history

   Do not whitelist real architecture violations just to pass CI.

15. Migrations

   Run:
   `scripts/test-migrations.ps1`

   For each service:
   - exactly one head unless intentionally documented
   - clean DB -> upgrade head
   - existing DB -> upgrade head
   - current == head
   - alembic check
   - existing round-trip/down tests where supported

   Preserve migration history; never squash production history casually.

16. OpenAPI contracts

   Capture approved baseline snapshots from the known-good build.

   Capture candidate snapshots.

   Run:
   `scripts/check-openapi-breaking.py`

   Review each removal/change.

   Do not regenerate the baseline merely because the candidate breaks it.

17. Authorization matrix

   Inspect the real routes and reconcile:
   `tests/security/authorization-matrix.yaml`

   Run through Gateway using dedicated QA tokens.

   Then add resource-ownership cases beyond role-only checks.

   A frontend hidden button is not an authorization test.

18. Event/messaging integration

   Against live RabbitMQ test:
   - publish
   - consume
   - delayed retry
   - max attempts -> DLQ
   - DLQ replay
   - duplicate event_id
   - consumer restart
   - publisher restart

   Verify outbox/inbox correctness survives process restarts.

19. Redis/idempotency integration

   Start at least two replicas of a mutation-serving service.

   Send the same stable Idempotency-Key concurrently to different replicas.

   Verify:
   - one side effect
   - replay/in-progress behavior
   - same key/different payload -> 409
   - durable Redis shared state is used

20. Failure/resilience tests

   Test actual dependency outages:
   - Identity/JWKS
   - Academic
   - Redis
   - RabbitMQ
   - MinIO/S3
   - email provider

   Verify Sprint 16 behavior:
   - finite timeout
   - bounded retry
   - no unsafe mutation retry without idempotency
   - circuit opens/recovery works
   - 503/fail closed where required
   - no cross-DB fallback

21. Coverage

   Add pytest-cov to service CI where missing.

   Target >=80% line coverage per service/shared library.

   Do not game coverage by excluding domain modules or replacing meaningful
   integration tests with line-only tests.

22. Browser E2E

   Integrate `tests/e2e`.

   Use dedicated staging Student/Teacher/Admin accounts.

   Keep baseline:
   - login
   - protected-route redirect
   - role workspace isolation
   - no auth tokens in Web Storage
   - recovery privacy

   Then automate the actual role workflows from:
   - tests/workflows/student.yaml
   - tests/workflows/teacher.yaml
   - tests/workflows/admin.yaml

   Add stable `data-testid` only where accessible role/name locators are not
   sufficiently stable.

23. Student workflow

   Automate:
   - login
   - own academic context
   - timetable
   - attendance
   - published Learning resource
   - assigned quiz attempt/submit
   - result visibility
   - notifications
   - Facility booking request
   - logout

24. Teacher workflow

   Automate:
   - login
   - assigned sections
   - Attendance create/finalize
   - Learning publish
   - quiz publish/assign
   - Student attempt grading
   - permitted notification targeting
   - Admin operation rejection

25. Admin workflow

   Automate:
   - login
   - academic master data
   - schedule creation/conflict
   - Facility approval
   - Reporting dashboard
   - Platform audit/jobs
   - internal Gateway route remains blocked

26. Frontend

   Run:
   - npm run typecheck
   - npm run lint
   - npm run test
   - npm run build

   Add focused component/unit tests for logic not efficiently covered by
   Playwright.

27. Security regression

   Sprint 18 security suite remains mandatory:
   - password policy
   - lockout
   - HttpOnly refresh
   - Origin protection
   - CSP/headers
   - upload checks
   - secret/dependency/container scans
   - DB/S3/RabbitMQ least privilege

28. CI

   Reconcile `.github/workflows/quality.yml` with existing workflows.

   Prefer reusable/matrix jobs over duplicated installs.

   Publish:
   - JUnit XML
   - coverage reports
   - Playwright report
   - QA summary
   - OpenAPI candidate snapshots

   Do not publish secrets/tokens.

29. Aggregate runner

   Make:
   `scripts/run-sprint19.ps1`

   work in the real repository for offline/static tests.

   Make:
   `scripts/run-sprint19.ps1 -Live -E2E`

   work against QA/staging.

30. Quality gates

   Reconcile `tests/QUALITY_GATES.yaml`.

   Required gate skips are failures unless an explicit release exception is
   documented with:
   - owner
   - reason
   - risk
   - expiry/review date

31. Do not solve Sprint 19 by:
   - replacing PostgreSQL race tests with SQLite
   - making tests order-dependent
   - reaching into another service database for test setup
   - weakening assertions to broad 2xx/4xx ranges unnecessarily
   - regenerating contract baselines after unexplained breaking changes
   - hiding failed tests with permanent skips
   - using production credentials/data
   - disabling RBAC/security for E2E convenience
   - adding fixed sleeps where bounded condition polling works

At completion report:
- existing vs new test counts per service
- coverage per service
- PostgreSQL concurrency results
- migration results for all ten services
- contract snapshot changes
- authorization matrix results
- event retry/DLQ/idempotency results
- failure/resilience test results
- frontend results
- Gateway results
- security results
- Student E2E result
- Teacher E2E result
- Admin E2E result
- aggregate QA totals
- any remaining skipped/xfail required scenario and justification
