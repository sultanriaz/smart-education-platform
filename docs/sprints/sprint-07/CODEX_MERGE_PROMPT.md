Integrate Sprint 7 Learning Resource Service into the current Smart Education Platform repository.

First inspect all existing Sprint 1-6 services and contracts. Do not blindly preserve placeholder integration paths from the Sprint 7 package.

Tasks:
1. Merge `services/learning-service`, `docker-compose.learning.yml`, and Learning CI without deleting existing work.
2. Verify and adapt the real Identity JWKS URL, issuer, audience, algorithm and access-token claim format.
3. Inspect Academic Service and adapt `HttpAcademicClient` to its real section/course assignment and enrollment APIs. Do not access academic_db and do not import Academic ORM/domain models.
4. Inspect Notification Service and adapt `app/workers/outbox_relay.py` to the actual internal event contract and internal-token convention.
5. Preserve Learning ownership boundaries: learning_db and object storage only.
6. Verify FILE/LINK/VIDEO/NOTE version behavior, publish/archive lifecycle, role boundaries, student target visibility, access logging and deterministic recommendations.
7. Run Learning migrations against PostgreSQL: upgrade, downgrade base, re-upgrade, alembic check.
8. Run Learning tests, Ruff and formatting checks.
9. Build/run Docker Compose and verify /health, /ready and /docs.
10. Run a live integration smoke flow where environment permits: teacher creates resource for assigned section, uploads/adds a version, publishes; enrolled student can see/download it; unrelated student cannot; published event can be accepted by Notification Service.
11. Run regression tests for existing Identity, Academic, Attendance, Scheduling, Notification and Facility services.
12. Do not weaken authorization or service boundaries merely to pass tests.

Report exact contract adaptations, exact test counts/results, migration results, Docker results, unresolved assumptions, and commands needed for the developer to reproduce verification.
