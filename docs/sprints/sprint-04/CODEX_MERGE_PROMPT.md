Merge and integrate the Sprint 4 Scheduling Service package that has been extracted into this repository root.

First inspect the existing Identity, Academic, and Attendance services. Do not rewrite them.

Tasks:
1. Review `services/scheduling-service`, `docker-compose.scheduling.yml`, and the Scheduling CI workflow.
2. Compare Scheduling's JWT/JWKS configuration with the actual Identity contract and align issuer, audience, algorithm, JWKS route, and claim names if necessary.
3. Compare `app/clients/academic.py` with the actual Academic Service routes and response shapes. Adjust only the HTTP client/config contract as needed. Do not access `academic_db` directly and do not import Academic persistence/domain models.
4. Confirm ports do not conflict with the existing platform. Preserve Scheduling API on 8004 where possible and change only if the repository already owns that port.
5. Run Scheduling migrations against PostgreSQL: upgrade head, downgrade base, upgrade head, alembic check.
6. Run `pytest -q`, including `tests/test_postgres_concurrency.py` with a real PostgreSQL test URL.
7. Run `ruff check .` and `ruff format --check .`; fix issues without weakening rules.
8. Build and run `docker-compose.scheduling.yml`; verify `/health`, `/ready`, and `/docs`.
9. Run authenticated smoke tests using the real Identity JWKS and Academic Service: admin schedule creation, teacher assignment enforcement, student `/timetable/me`, conflict rejection, occurrence cancellation, and rescheduling.
10. If there is a shared gateway/combined Compose file, integrate Scheduling without changing service database ownership.
11. Do not add cross-service database foreign keys or direct DB reads.
12. Report every file changed, exact test counts, migration results, Docker results, integration fixes, and any unresolved issue.
