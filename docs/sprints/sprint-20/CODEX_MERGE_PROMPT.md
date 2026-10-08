Integrate Sprint 20 Performance & Scalability Engineering into the current Smart
Education Platform.

FIRST inspect the actual merged Sprints 1–19. Preserve all correctness,
security, migration, RBAC, and distributed-system guarantees.

The goal is to measure and improve performance without weakening behavior.

1. Install performance tooling

   Integrate:
   - `libs/python/smartedu_perf`
   - `requirements.performance.txt`

   Run the shared package tests before any load testing.

2. Reconcile routes

   Inspect final Gateway/OpenAPI contracts.

   Update Locust endpoint defaults only where the generated Sprint 20 baseline
   differs from the real routes.

   Keep stable Locust task names because result comparison uses them.

3. QA data

   Build deterministic, disposable performance fixtures for:
   - Student
   - Teacher
   - Admin
   - Academic enrollment
   - section/timetable
   - Attendance session
   - published Learning resources
   - Assessment assignment
   - Facility records
   - notification target

   Never use production data.

4. Authentication

   Use real Sprint 18 login + HttpOnly refresh-cookie behavior for long runs.

   Do not create long-lived bypass tokens or disable lockout/Origin protection.

   Ensure the QA identities are allowed to perform expected load without
   triggering false brute-force protection from incorrect credentials.

5. Baseline load

   Run:
   - smoke
   - baseline

   Record:
   - exact commit
   - exact replica counts
   - exact DB pool settings
   - exact environment
   - Locust stats/history
   - performance evaluation JSON

6. SRS acceptance

   Run `srs-500`.

   Prove:
   - at least 500 concurrent virtual users were sustained
   - representative 75/20/5 Student/Teacher/Admin mix
   - normal p95 <= 3000 ms
   - Attendance p95 <= 2000 ms
   - Notification end-to-end p95 <= 5000 ms
   - error rate <= 1%

   Do not claim success merely because the test command ran.

7. Attendance write performance

   Inspect the real Attendance mutation API.

   Configure a disposable session/roster and run the dedicated
   `AttendanceMutationUser`.

   Keep the data valid for repeated writes or rebuild the fixture between runs.

   Report:
   - p50/p95/p99
   - rps
   - errors
   - DB lock waits
   - query plan

8. Notification end-to-end performance

   Reconcile `measure-notification-latency.py` with the real Notification
   campaign/event contract.

   Measure from source request/event to recipient inbox visibility.

   Include:
   - source service outbox
   - RabbitMQ
   - Notification consumer
   - persistence
   - recipient read API

   Calculate p95 over a meaningful sample.

9. Browser/page timing

   Integrate Sprint 20's Playwright performance spec with Sprint 19 E2E.

   Expand it to the real high-value Student/Teacher/Admin pages.

   The SRS page target is p95 <= 3s.

   Measure navigation/render readiness, not just raw HTTP response time.

10. PostgreSQL instrumentation

    Use:
    - `performance-diagnostics.sql`
    - `pg-stat-statements.sql`
    - `index-review.sql`
    - `capture-db-performance.ps1`

    Enable `pg_stat_statements` in QA using the deployment-supported method.

    Capture evidence during the baseline and 500-user runs.

11. Query plans

    Identify the highest total-cost and highest p95 query paths.

    For each optimized query:
    - capture EXPLAIN/BUFFERS before
    - make one measured change
    - capture after
    - rerun endpoint load
    - run correctness/concurrency regression

    Do not optimize synthetic queries that are not on actual hot paths.

12. Indexing

    Inspect all ten service migrations and queries.

    Add only evidence-backed indexes through the owning service Alembic history.

    High-priority families:
    - Identity user/refresh/RBAC lookup
    - Academic enrollment/section/assignment
    - Attendance section/session/student summary
    - Scheduling interval conflicts
    - Notification inbox/outbox/delivery
    - Facility overlap/availability
    - Learning targeting/version lookup
    - Assessment assignment/attempt/grading
    - Reporting dimension/date lookup
    - Platform audit/job lookup

    Re-run Sprint 19 PostgreSQL races after index changes.

13. ORM/N+1

    Instrument query count on slow endpoints.

    Remove:
    - N+1 lazy loads
    - per-row cross-repository loops
    - unbounded collections
    - repeated identical lookups

    Preserve authorization filters.

14. Pagination

    Review list/report endpoints reached by load tests.

    Add bounded pagination where an endpoint can return unbounded rows.

    Preserve API contracts or version them according to Sprint 16 contract rules.

15. Connection pools

    Reconcile:
    `tests/performance/config/connection-budgets.yaml`

    with real Sprint 17 settings and candidate replica counts.

    Run:
    `python scripts/check-connection-budget.py`

    Ensure:
    sum(replicas * (pool_size + max_overflow))
    leaves safe headroom under the physical PostgreSQL connection limit.

    Do not solve latency by blindly increasing every pool.

16. Cache strategy

    Read `CACHE_STRATEGY.md`.

    Use `redis-cache` only for safe derived/repeatable reads.

    For every cache:
    - bounded TTL
    - namespace
    - invalidation/refresh
    - max payload size
    - hit-rate measurement
    - stale-data correctness test

    Never move booking conflicts, attendance truth, attempt limits, or RBAC truth
    into a disposable cache.

17. Reporting architecture

    Ensure dashboards query Reporting's event-driven read model.

    Do not introduce synchronous runtime fan-out from Reporting to all domain
    services just to improve feature completeness.

18. RabbitMQ and workers

    Measure:
    - publish confirms/sec
    - queue depth
    - oldest-message age
    - consumer throughput
    - retries/DLQ
    - outbox backlog

    Scale:
    - Notification workers
    - Reporting consumers
    - outbox publishers

    independently from web/API replicas.

19. Redis benchmark

    Use the supplied Redis diagnostic benchmark.

    Record:
    - operations/sec
    - avg
    - p95
    - p99
    - failures

    Benchmark cache and durable Redis separately if they are separate targets.

20. RabbitMQ benchmark

    Use the supplied diagnostic benchmark in isolated QA.

    It is not an SRS acceptance test.

    Do not run destructive/high-volume broker benchmarks on production.

21. S3/MinIO

    Measure Learning resource flow and use the supplied object benchmark for
    diagnosis.

    Keep bucket authorization/private access from Sprint 18.

22. Horizontal scaling

    Read `SCALABILITY_PLAN.md`.

    Test:
    - single-replica reference
    - included candidate topology
    - adjusted topology based on actual bottlenecks

    Record p95/rps/error/CPU/memory/DB connections for each.

    Do not add replicas when the bottleneck is DB lock contention or pool
    exhaustion.

23. Stress

    Run:
    - stress-750
    - stress-1000

    Identify the first saturation point.

    Report:
    - max stable concurrency
    - max stable rps
    - first failing dependency
    - failure mode
    - recovery behavior

24. Soak

    Run at least `soak-250`.

    Look for trends in:
    - process RSS
    - DB connections
    - pool checkout wait
    - Redis memory
    - RabbitMQ queue age
    - object client connections
    - p95/error drift

    Extend duration if 30 minutes is too short to establish a trend.

25. Performance regression

    Store approved baseline evaluation JSON.

    Run:
    `scripts/compare-performance.py`

    Default relative gates:
    - >20% p95 regression fails
    - >20% rps drop fails
    - error increase above 1% fails

    Absolute SRS budgets override relative comparison.

26. CI

    Reconcile `.github/workflows/performance.yml` with current CI.

    Keep weekly baseline load on a dedicated staging/performance target.

    Heavy SRS/stress/soak runs should be manual or isolated scheduled jobs.

    Do not hit arbitrary/production URLs from untrusted PRs.

27. Preserve Sprint 19 quality

    After every optimization, rerun:
    - affected service unit/integration tests
    - PostgreSQL race tests
    - migration tests
    - authorization tests
    - Gateway tests
    - frontend tests
    - Sprint 18 security regression

28. Do not solve Sprint 20 by:
    - weakening RBAC
    - caching correctness-critical state
    - removing audit/outbox writes
    - disabling transaction locks
    - changing isolation guarantees without proof
    - returning stale assessment/attendance data where correctness matters
    - disabling password hashing cost
    - issuing insecure long-lived JWTs
    - increasing DB max_connections without capacity analysis
    - adding every possible index
    - hiding failures from Locust
    - measuring only localhost and calling it production capacity

At completion report:
- exact hardware/container resources used
- exact topology/replicas
- exact DB pool settings
- baseline results
- 500-user results
- general p50/p95/p99
- Attendance read/write p50/p95/p99
- Notification end-to-end p95
- error rate and rps
- hottest SQL before/after
- indexes added/removed and evidence
- cache changes/hit rates
- connection-budget result
- Redis benchmark
- RabbitMQ throughput/lag
- object-storage result
- single-replica vs scaled comparison
- stress saturation point
- soak trends
- all performance regressions fixed/accepted
- Sprint 19 correctness/security regression totals
- any remaining bottleneck with evidence
