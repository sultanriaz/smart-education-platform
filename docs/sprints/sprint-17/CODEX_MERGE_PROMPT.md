Integrate Sprint 17 Data & Messaging Infrastructure Hardening into the current
Smart Education Platform.

FIRST inspect the actual merged Sprints 1–16. Do not replace proven service
persistence/event code blindly.

The final result must preserve independent service/database ownership while
hardening PostgreSQL, Redis, RabbitMQ, object storage, migrations, backups,
retention, and workers.

1. Shared package

   Integrate:
   `libs/python/smartedu_infra`

   It depends on Sprint 16 `smartedu-contracts`.

   Install both packages in every service image/environment.

2. Local infrastructure

   Integrate:
   `docker-compose.infrastructure.yml`

   Start and verify:
   - PostgreSQL 16
   - redis-cache
   - redis-durable
   - RabbitMQ
   - MinIO
   - MinIO bootstrap

   If existing per-service Compose stacks already run conflicting DB/Redis/MinIO
   containers, reconcile them into one coherent local topology rather than
   running duplicate infrastructure.

3. Database-per-service ownership

   Ensure the ten logical databases/service logins are enforced.

   A service must receive only its own DB credential.

   Search for and remove:
   - cross-service DATABASE_URL use
   - direct SQL against another service DB
   - shared ORM metadata
   - another service repository import

4. SQLAlchemy connection pools

   Inspect each existing service DB module and merge the Sprint 17 pool behavior
   without creating duplicate Engines.

   Required:
   - pool_pre_ping
   - bounded pool_size
   - bounded max_overflow
   - finite pool_timeout
   - recycle
   - PostgreSQL statement timeout
   - UTC session timezone
   - DB application_name

   Keep SQLite test-specific engines working.

5. Migrations

   Preserve every service's current Alembic history.

   Run:
   - heads
   - upgrade head
   - current
   - schema drift/autogenerate no-op checks
   - downgrade/round-trip where the service supports it

   Production application replicas must not independently race to migrate.

   Design one deployment migration job per service.

6. Seeds

   Inventory seed scripts.

   Keep bootstrap seeds idempotent.

   Separate:
   - required RBAC/master data
   - institution-specific data
   - demo data

   Demo data must not run in production.

7. Redis

   Migrate Sprint 16 idempotency to:

   `redis-durable`

   Configure:
   `IDEMPOTENCY_REDIS_URL=redis://redis-durable:6379/1`

   Use `redis-cache` only for disposable TTL-bound derived values.

   Do not put business source-of-truth state into Redis.

8. RabbitMQ

   Use RabbitMQ as the cross-service event transport.

   Bootstrap:
   - smartedu.events
   - smartedu.retry
   - smartedu.dlx
   - durable service queues
   - durable retry queues
   - durable DLQs

   Review `contracts/event-subscriptions.json` against the real event catalog.

   Keep only real consumer subscriptions.

9. Existing outbox/inbox code

   Inspect all current event code.

   Preserve transactional outbox/inbox semantics and race protection.

   Adapt transport to `RabbitEventBus` or equivalent.

   Do NOT replace a service-owned outbox with direct publish inside a domain
   transaction.

   Domain write + outbox row must commit together.

   Mark published only after publisher confirmation.

10. Retry/DLQ

   Verify handler failures:
   - go to retry exchange
   - wait configured TTL
   - return to main queue
   - increment attempt
   - eventually reach DLQ

   Verify no hot-loop requeue.

   Verify `rabbitmq_dlq_replay.py`.

11. EventEnvelope

   Preserve Sprint 16:
   - event_id
   - event_type
   - event_version
   - UTC occurred_at
   - correlation_id
   - causation_id

   Consumers must deduplicate by event_id.

12. Workers

   Separate web/API processes from long-running event workers.

   Implement each worker with the service EventRouter and
   `run_event_worker(...)` or equivalent.

   Add Docker/Compose worker services where needed.

   Likely workers:
   - Notification delivery/event ingestion
   - Reporting projection ingestion
   - Platform audit/event ingestion
   - any existing Facility/Assessment/Learning outbox publisher
   - other actual service outbox publishers found in repository

   Do not invent workers for services that have no asynchronous task.

13. Learning object storage

   Inspect Sprint 7's current storage implementation.

   Converge it on the shared S3-compatible ObjectStorage helper or preserve its
   existing correct client if better.

   Required:
   - private bucket
   - path traversal protection
   - file size/type validation remains domain-owned
   - short-lived presigned URLs if used
   - no binary BLOB persistence in PostgreSQL
   - resource/version metadata remains in learning_db

14. Platform/Reporting storage

   If Sprint 10 imports/exports or Sprint 9 report exports currently store large
   generated files in the DB/local filesystem, migrate them to:
   - platform-imports
   - platform-exports
   - report-exports

   Store only keys/metadata/status in the owning DB.

15. Backups

   Run local PostgreSQL backups and restore drills.

   Run object storage backup/restore with checksum validation.

   Report exact restore results.

   Do not call backup complete merely because pg_dump succeeded.

16. Retention

   Reconcile `contracts/retention-policy.yaml` with real table names/states.

   Add service-specific retention jobs/migrations only after validating terminal
   state predicates.

   Never delete:
   - unprocessed outbox
   - active jobs
   - inbox dedup records inside redelivery horizon
   - live Learning resource content

17. Indexes

   Inspect real SQLAlchemy models, repository queries, Postgres EXPLAIN plans,
   and current indexes.

   Add only justified indexes via each service's Alembic migrations.

   Pay special attention to:
   - uniqueness enforcement
   - foreign/reference UUID lookup
   - section/student/Teacher lookup
   - schedule conflict predicates
   - booking overlap predicates
   - notification unread/delivery lookup
   - assessment assignment/attempt lookup
   - audit/report timestamp lookup

   Re-run PostgreSQL-specific concurrency tests after index/migration changes.

18. Environment separation

   Use separate dev/staging/prod:
   - DB credentials/databases
   - Redis
   - RabbitMQ vhost/credentials
   - buckets
   - secrets

   Production infrastructure ports must not be public.

19. Docker

   Modify service Dockerfiles to install:
   - smartedu-contracts
   - smartedu-infra

   Use repository-root build context or build wheels in CI.

   Do not depend on host bind mounts for production.

20. Tests

   Run:
   `cd libs/python/smartedu_infra && pytest -q`

   Then all service suites, Gateway, frontend typecheck/lint/test/build.

   Add integration tests for:
   - PostgreSQL connections/pool exhaustion behavior
   - Redis cache TTL
   - durable Redis idempotency across replicas
   - RabbitMQ publish/consume
   - delayed retry
   - DLQ
   - DLQ replay
   - duplicate event
   - outbox crash/restart safety
   - MinIO upload/download/private access
   - backup/restore
   - migration serialization

21. Full E2E

   Run Student, Teacher, and Admin flows after infrastructure migration.

22. Do not solve Sprint 17 by:
   - merging service databases
   - granting one DB user access to all DBs
   - using Redis as the source of truth
   - publishing events before the domain transaction commits
   - immediate infinite RabbitMQ requeue loops
   - storing private object-storage buckets publicly
   - auto-running migrations from every production replica
   - committing infrastructure passwords
   - deleting data with unreviewed retention SQL

At completion report:
- exact DB URL/user per service
- exact pool settings
- migration status/heads per service
- seed scripts classified
- Redis usages and DB numbers
- RabbitMQ exchanges/queues/subscriptions
- outbox/inbox adaptations per service
- worker processes added
- storage migrations
- backup and restore drill results
- retention jobs
- indexes added and why
- shared package test total
- each service test total
- Docker results
- Student/Teacher/Admin E2E results
- remaining infrastructure assumptions
