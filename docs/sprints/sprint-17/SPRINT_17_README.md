# Sprint 17 — Data & Messaging Infrastructure Hardening

Sprint 17 turns the distributed services from Sprints 1–16 into a more
production-oriented data platform.

It does not merge service databases and does not introduce a new business
domain.

## Major deliverables

### Shared `smartedu-infra` Python package

Location:

```text
libs/python/smartedu_infra
```

Provides reusable infrastructure helpers for:

- bounded SQLAlchemy connection pools
- PostgreSQL UTC/session configuration
- Redis cache access
- RabbitMQ event transport
- delayed message retries
- per-service dead-letter queues
- EventEnvelope transport from Sprint 16
- service event workers
- service-owned outbox publishing
- S3-compatible object storage
- safe object-key handling
- presigned URLs
- data-retention helpers
- infrastructure health checks
- canonical service/database naming

The package contains no domain ORM models.

### PostgreSQL

Local development receives one PostgreSQL 16 server with ten logical databases
and ten independent service accounts:

```text
identity_db      -> identity_svc
academic_db      -> academic_svc
attendance_db    -> attendance_svc
scheduling_db    -> scheduling_svc
notification_db  -> notification_svc
facility_db      -> facility_svc
learning_db      -> learning_svc
assessment_db    -> assessment_svc
reporting_db     -> reporting_svc
platform_db      -> platform_svc
```

This is resource-efficient locally while preserving database-per-service
ownership.

Production may split these across managed clusters without changing service
ownership.

### Redis separation

Two Redis instances are provided.

`redis-cache`:

```text
volatile
no AOF
allkeys-lru
bounded cache memory
```

Use only for safe derived/cache data.

`redis-durable`:

```text
AOF every second
RDB snapshots
persistent volume
noeviction
```

Use for Sprint 16 distributed idempotency and other explicitly designed
short-lived correctness state.

Business source-of-truth records stay in PostgreSQL.

### RabbitMQ

RabbitMQ is the Sprint 17 event transport.

Exchanges:

```text
smartedu.events   topic event exchange
smartedu.retry    retry exchange
smartedu.dlx      dead-letter exchange
```

Each consumer service gets:

```text
<service>.events
<service>.events.retry
<service>.events.dlq
```

A failed message is not immediately hot-looped.

Instead:

```text
main queue
    ↓ failure
retry exchange
    ↓
retry queue
    ↓ TTL delay
event exchange
    ↓
main queue
```

After the configured maximum attempts, it moves to the service DLQ.

Default:

```text
EVENT_RETRY_DELAY_MS=5000
EVENT_MAX_DELIVERY_ATTEMPTS=5
```

The included DLQ replay tool can selectively republish failed messages after the
underlying defect has been fixed.

### At-least-once delivery

RabbitMQ delivery is treated as at least once.

Correctness requires:

- Sprint 16 `event_id`
- service-owned inbox/deduplication
- idempotent handlers
- transactions around business writes
- service-owned outbox records

The shared OutboxPublisher never imports another service's ORM schema.

### Object storage

MinIO provides S3-compatible local development storage.

Private buckets:

```text
learning-resources
platform-imports
platform-exports
report-exports
```

Learning resources are versioned at the bucket level locally as an extra safety
layer.

Application metadata remains in the owning service database.

PostgreSQL should not become a large-file/BLOB store.

### Connection pools

Every service can configure:

```text
DB_POOL_SIZE
DB_MAX_OVERFLOW
DB_POOL_TIMEOUT_SECONDS
DB_POOL_RECYCLE_SECONDS
DB_STATEMENT_TIMEOUT_MS
DB_APPLICATION_NAME
```

The shared engine uses:

```text
pool_pre_ping
finite pool timeout
bounded overflow
connection recycling
UTC PostgreSQL sessions
statement timeout
application_name
```

### Migrations

Sprint 17 establishes:

```text
one Alembic history per service
one migration job per service release
no production migration race between application replicas
```

A generic PowerShell migration runner is included.

### Seeding

Seed scripts remain separate from schema migrations.

Seeds must be:

- deterministic
- idempotent
- safe to rerun
- appropriate to the environment

Production must not receive demo users through seed automation.

### Backups and restore

Included:

```text
backup-databases.ps1
restore-database.ps1
verify-backup-restore.ps1
object_storage_backup.py
object_storage_restore.py
```

PostgreSQL backups use custom `pg_dump` format.

The restore-verification script restores into a disposable database first.

Object-storage backups include SHA-256 checksums.

### Retention

Included retention policy covers:

- published outbox records
- processed inbox records
- notification-delivery history
- platform jobs
- audit events
- temporary imports/exports

Learning resources are not automatically deleted by generic retention scripts.

Object-storage retention defaults:

```text
platform-imports   7 days
platform-exports  30 days
report-exports    14 days
```

The cleanup script is dry-run unless `--apply` is provided.

### Diagnostics and indexing

PostgreSQL diagnostics report:

- connection states
- long-running queries
- sequential/index scans
- dead tuples
- index usage
- large tables
- invalid indexes

Sprint 17 intentionally does not generate speculative indexes without inspecting
the real merged service schemas.

Codex must inspect the actual query patterns and migrations before adding
service-specific indexes.

## Local infrastructure

Copy:

```text
.env.infrastructure.example
```

to:

```text
.env.infrastructure
```

Then:

```powershell
.\scripts\start-infrastructure.ps1
```

Local endpoints:

```text
PostgreSQL      localhost:55432
Redis cache     localhost:56379
Redis durable   localhost:56380
RabbitMQ AMQP   localhost:5672
RabbitMQ UI     localhost:15672
MinIO API       localhost:59000
MinIO console   localhost:59001
```

All ports are configurable in `.env.infrastructure`.

Production should not expose these infrastructure ports publicly.

## Per-service bridges

All ten services receive:

```text
services/<service>/app/sprint17.py
```

These supply factories for:

- database settings/engine
- Redis settings
- messaging settings
- Rabbit event bus
- object storage

Codex should reconcile each existing service's infrastructure client with these
factories rather than creating duplicate pools/clients.

## Relationship to Sprint 16

Sprint 17 builds directly on Sprint 16:

```text
Sprint 16
  EventEnvelope
  correlation IDs
  service authentication
  idempotency
  resilience contracts
        │
        ▼
Sprint 17
  PostgreSQL ownership
  Redis topology
  RabbitMQ transport
  outbox workers
  S3 storage
  backups
  retention
  migrations
```

Sprint 16 `IDEMPOTENCY_REDIS_URL` should point to `redis-durable`, not
`redis-cache`.
