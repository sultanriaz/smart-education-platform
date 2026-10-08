Integrate Sprint 6 Facility Service into the existing Smart Education Platform repository.

First inspect the actual merged repository and all Sprint 1-5 contracts. Do not assume package examples are exact.

Tasks:

1. Preserve every existing service and its database ownership.
2. Integrate `services/facility-service`, `docker-compose.facility.yml`, and Facility CI.
3. Run Facility tests, lint, formatting checks, migrations, and Docker smoke tests.
4. Inspect Sprint 4 Scheduling's room model and API. Make Facility Service the authoritative owner of facility/room identity and availability. Do not let Scheduling query facility_db.
5. Adapt Scheduling through HTTP/internal contracts as needed:
   - validate facility existence where appropriate
   - create/cancel external reservations through Facility Service
   - keep teacher/section/time conflict rules inside Scheduling
   - use stable idempotency/source reference IDs for occurrences
6. Inspect Sprint 5 Notification internal event envelope. Add/adapt an outbox relay or mapping so Facility events can create user notifications without direct DB access.
7. Ensure booking-approved/rejected/cancelled events target the requester correctly.
8. Verify Identity JWT/JWKS settings against the real Identity Service contract.
9. Check for port collisions. Facility defaults are API 8006 and PostgreSQL 5439; change only if repository reality requires it and update all docs/config consistently.
10. Run regression tests for Identity, Academic, Attendance, Scheduling, Notification, and Facility where the local environment supports them.
11. Run a combined smoke test covering facility create -> booking -> approval -> availability -> scheduling conflict -> cancellation.
12. Do not weaken service boundaries to make tests pass.

When finished report:
- files changed
- any contract adaptations
- test counts/results per service
- Alembic results
- Docker results
- combined smoke-test results
- unresolved issues
- exact startup commands
