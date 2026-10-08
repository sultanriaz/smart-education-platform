Integrate Sprint 8 Assessment Service into the current Smart Education Platform repository.

FIRST inspect the actual implementations of Sprints 1-7. Do not assume their
contracts match this package exactly.

Preserve the distributed service boundaries:
- Assessment Service owns assessment_db only.
- Never query identity_db or academic_db.
- Never import another service's ORM models.
- Use HTTP/event contracts.

Required work:

1. Inspect services/identity-service and reconcile:
   - JWKS endpoint
   - issuer
   - audience
   - algorithms
   - token type
   - subject UUID
   - role claim

2. Inspect services/academic-service and reconcile Assessment's AcademicClient:
   - section lookup
   - teacher-section assignment validation
   - student-section enrollment validation

3. Inspect services/notification-service and reconcile Assessment outbox relay:
   - event envelope
   - internal auth header/token
   - targeting conventions

4. Inspect services/learning-service. Do not create direct database coupling.
   If useful, document a future event contract between learning and assessment,
   but do not make Assessment depend on learning_db.

5. Preserve these Sprint 8 rules:
   - DRAFT/PUBLISHED/ARCHIVED quiz lifecycle
   - MCQ_SINGLE, TRUE_FALSE, SHORT_TEXT questions
   - immutable submission boundary
   - objective auto-grading
   - manual grading for subjective responses
   - attempt limits
   - open/due windows
   - student owns only their attempts
   - teacher assignment checked through Academic Service
   - student enrollment checked through Academic Service
   - transactional outbox

6. Expand tests where needed, especially:
   - JWT rejection and role boundaries
   - deadline/open-window behavior
   - attempt limit concurrency on PostgreSQL
   - duplicate quiz assignment
   - submission immutability
   - objective grading
   - subjective grading
   - grade audit
   - transaction rollback
   - Academic Service outage behavior
   - Notification outbox compatibility

7. Run:
   - ruff check
   - ruff format --check
   - pytest
   - PostgreSQL-specific tests
   - alembic upgrade head
   - alembic downgrade base
   - alembic upgrade head
   - alembic check
   - docker build
   - /health
   - /ready
   - OpenAPI
   - end-to-end teacher -> student -> grade smoke flow

8. Run regression tests for Sprints 1-7 after integration.

Do not weaken authorization or service boundaries merely to make tests pass.

At completion report:
- contract adaptations
- exact test totals
- migration results
- Docker results
- end-to-end smoke results
- any unresolved assumptions
