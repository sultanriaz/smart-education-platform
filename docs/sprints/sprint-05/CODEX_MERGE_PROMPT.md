Integrate Sprint 5 Notification Service from the files already extracted into this repository.

First inspect the current Identity, Academic, Attendance, and Scheduling services and compare their actual contracts with the new Notification Service. Do not rewrite completed services unnecessarily.

Requirements:

1. Keep `services/notification-service` independently deployable with its own `notification_db`.
2. Do not add cross-service ORM imports or direct database access.
3. Verify/adapt the Identity JWKS configuration to exactly match the working JWT pattern already used by Academic/Attendance/Scheduling.
4. Verify `app/clients/identity.py` against the real Identity endpoints. Keep any adjustments isolated to that client/config.
5. Verify `app/clients/academic.py` against the real Academic section-roster endpoint. Keep adjustments isolated to that client/config.
6. Integrate Scheduling and Attendance transactional outboxes by adding/using an upstream relay that POSTs envelopes to `/api/v1/internal/events`. Notification Service must not read their DBs.
7. For Sprint 4 `schedule.occurrence_changed`, ensure the published event has enough targeting context (`section_id`, `teacher_user_id`) or make the relay populate explicit `targets`. Prefer a small non-breaking upstream event-payload enhancement.
8. For Attendance low-attendance events, ensure `student_user_id` or `targets.user_ids` is present.
9. Validate Docker Compose coexistence and port conflicts with all existing services.
10. Use secure local secrets through environment variables; do not commit real tokens.
11. Run and report:
   - pytest -q
   - ruff check .
   - ruff format --check .
   - alembic upgrade head
   - alembic downgrade base
   - alembic upgrade head
   - alembic check
   - Docker image build
   - `/health`, `/ready`, and `/docs` smoke tests
   - internal-event idempotency test
   - notification flow smoke test from one real upstream outbox event if feasible
12. Fix integration issues you discover, but preserve service ownership boundaries.
13. When finished, give exact test counts, migration results, Docker results, contract changes, and unresolved assumptions.
