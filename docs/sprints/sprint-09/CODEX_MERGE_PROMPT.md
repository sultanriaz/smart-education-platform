Integrate Sprint 9 Reporting & Analytics Service into the current Smart Education
Platform repository.

FIRST inspect the actual implementations of Sprints 1-8.

Do not assume this package's event names or payload shapes match the repository.

Architecture rule:
Reporting Service must not query another service's operational database and must
not import another service's ORM models. It consumes explicit APIs/events only.

Required integration work:

1. Identity
   Reconcile JWKS URL, issuer, audience, algorithm, access token type, user ID
   claim, and admin role claim.

2. Academic Service
   Inspect its actual outbox/events. Add/adapt reporting consumers for:
   - enrollment created/activated
   - enrollment dropped/cancelled
   - program/section metadata if available

3. Attendance Service
   Inspect its actual outbox payloads and map:
   - attendance creation
   - attendance correction/update
   - section/course/session/student identifiers
   Preserve Attendance Service's real percentage semantics exactly.

4. Scheduling Service
   Reconcile actual schedule/occurrence event names and payloads.

5. Notification Service
   Reconcile delivery event identifiers, channels and status vocabulary.

6. Facility Service
   Reconcile booking lifecycle events and facility identifiers.

7. Assessment Service
   Reconcile `assessment.attempt_graded` (or actual equivalent).
   If the existing event lacks course/section/quiz identifiers needed for
   reporting, improve the source event payload without creating DB coupling.

8. Wire source transactional-outbox relays to Reporting Service using the actual
   repository conventions. A Reporting failure must never roll back a source
   service's business transaction.

9. Preserve idempotency:
   - duplicate event_id must not double count
   - update/correction events must update existing logical projections
   - PostgreSQL constraints must protect concurrent duplicate delivery

10. Expand tests:
   - JWT admin authorization
   - internal token rejection
   - duplicate event ingestion
   - concurrent duplicate event ingestion on PostgreSQL
   - attendance correction projection
   - facility status progression
   - notification status progression
   - assessment re-grade projection update
   - enrollment drop projection
   - CSV export
   - snapshot generation
   - dashboard calculations

11. Run:
   - ruff check
   - ruff format --check
   - pytest
   - PostgreSQL race tests
   - alembic upgrade head
   - alembic downgrade base
   - alembic upgrade head
   - alembic check
   - docker build
   - /health
   - /ready
   - OpenAPI
   - cross-service event smoke test
   - regression tests for Sprints 1-8

12. Do not weaken existing service boundaries or authorization to make tests pass.

At completion report:
- every event contract adaptation
- exact test totals
- migration results
- Docker results
- cross-service smoke results
- any unresolved analytics/data-quality assumptions
