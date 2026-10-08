Integrate Sprint 10 Platform Operations Service into the current Smart Education
Platform repository.

FIRST inspect Sprints 1-9. Do not assume this package's integration contracts
exactly match the repository.

Hard architecture rules:
- Platform Service owns platform_db only.
- Never query another service database.
- Never import another service's ORM models.
- Audit/search are projections, not authoritative domain state.
- Reporting and Platform failures must not roll back source business operations.

Required integration:

1. Identity
   Reconcile the actual JWT/JWKS contract:
   - endpoint
   - issuer
   - audience
   - algorithms
   - access token type
   - subject/user UUID
   - roles

2. Notification
   Reconcile Platform support-ticket outbox events with the actual Sprint 5
   Notification internal event envelope and targeting mechanism.

3. Source events
   Inspect Sprints 1-9 and add compatible outbox relay targets or event fan-out
   for Platform Service where appropriate.

   Prioritize:
   - Academic searchable course/program/section metadata
   - Facility searchable facility metadata
   - Learning searchable published resource metadata
   - optional Assessment searchable quiz metadata
   - audit events from administrative/security-sensitive mutations

4. Search authorization
   Ensure source search documents have explicit safe audience roles.
   Do not leak admin-only or student-private records.

5. Support
   Verify student/teacher ticket ownership rules and admin management.
   Add Notification integration for ticket creation, assignment, resolution and
   closure using the actual Notification Service contract.

6. Service health
   Seed or configure the registry for the actual services/ports in the merged
   repository.
   Health aggregation must use `/health` and `/ready` semantics already defined
   by each service.

7. Async jobs
   Reconcile Celery/Redis conventions with Sprint 5 if there is already shared
   worker infrastructure.
   Do not create database coupling for import/export.
   Enable remote import/export only for services that expose explicit internal
   endpoints and authorization.

8. Expand tests:
   - JWT failures and role boundaries
   - internal token rejection
   - duplicate event ingestion
   - PostgreSQL concurrent duplicate ingestion
   - search role filtering
   - search update/delete
   - audit projection
   - ticket ownership/internal notes
   - support lifecycle
   - public/private settings
   - feature flags
   - service health aggregation
   - worker job transitions
   - source-service outage behavior
   - Notification support event compatibility

9. Run:
   - ruff check
   - ruff format --check
   - pytest
   - PostgreSQL concurrency tests
   - alembic upgrade head
   - alembic downgrade base
   - alembic upgrade head
   - alembic check
   - Docker build
   - Redis/Celery worker smoke test
   - `/health`
   - `/ready`
   - OpenAPI
   - cross-service search event smoke test
   - support -> notification smoke test
   - service health aggregation smoke test
   - regression tests for Sprints 1-9

10. Do not weaken service boundaries or authorization to make tests pass.

At completion report:
- all contract adaptations
- exact test totals
- migration results
- Docker/Redis/Celery results
- source-event search smoke results
- support/notification smoke results
- service-health results
- unresolved assumptions
