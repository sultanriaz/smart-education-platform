# Sprint 17 Data & Messaging Architecture

## Local topology

```text
                         ┌────────────────────┐
                         │   API / Workers    │
                         └─────────┬──────────┘
                                   │
              ┌────────────────────┼─────────────────────┐
              │                    │                     │
              ▼                    ▼                     ▼
     ┌─────────────────┐  ┌────────────────┐  ┌──────────────────┐
     │ PostgreSQL 16   │  │ RabbitMQ       │  │ S3 / MinIO       │
     │                 │  │                │  │                  │
     │ identity_db     │  │ smartedu.events│  │ learning-        │
     │ academic_db     │  │ smartedu.retry │  │ resources        │
     │ attendance_db   │  │ smartedu.dlx   │  │ platform-imports │
     │ ... 10 DBs      │  │ per-service Q  │  │ platform-exports │
     └─────────────────┘  └────────────────┘  │ report-exports   │
              │                                └──────────────────┘
              │
              ├─────────────┐
              ▼             ▼
     ┌──────────────┐ ┌────────────────┐
     │ Redis cache  │ │ Redis durable  │
     │ volatile/LRU │ │ AOF/noeviction │
     └──────────────┘ └────────────────┘
```

The local environment uses one PostgreSQL server process to reduce laptop
resource usage, but creates ten independent databases and ten independent
least-privilege logins.

The architecture boundary is database ownership, not the number of physical
PostgreSQL machines.

Production may place those databases on one managed cluster or multiple
clusters. Services still receive only their own database credential.

## Redis separation

`redis-cache` is intentionally disposable:

```text
no persistence
allkeys-lru
bounded memory
```

Use it for:

- response/read-model cache
- safe derived values
- short-lived lookup data

Do not place idempotency records or correctness-critical state there.

`redis-durable` uses:

```text
AOF everysec
RDB snapshots
noeviction
persistent volume
```

Use it for:

- Sprint 16 distributed idempotency
- correctness-sensitive short-lived coordination where Redis is explicitly part
  of the design

Business source-of-truth data remains in PostgreSQL.

## RabbitMQ event flow

```text
Producer transaction
       │
       ▼
Service-owned outbox
       │
       ▼
Outbox publisher
       │
       ▼
smartedu.events (topic)
       │
       ├──────── notification-service queue
       ├──────── reporting-service queue
       └──────── platform-service queue
```

Consumer failure:

```text
main service queue
       │ handler failure
       ▼
smartedu.retry
       │
       ▼
service retry queue
       │ TTL delay
       ▼
smartedu.events
       │ retry.<service> routing key
       ▼
main service queue
```

After `EVENT_MAX_DELIVERY_ATTEMPTS`:

```text
smartedu.dlx
       │
       ▼
<service>.events.dlq
```

This avoids hot-loop `requeue=True` behavior.

## Delivery semantics

RabbitMQ delivery is treated as **at least once**.

Correctness comes from:

- EventEnvelope `event_id`
- consumer inbox/deduplication
- idempotent handlers
- service-owned transactions

A broker acknowledgment is sent only after the handler returns successfully, or
after the failed message has been durably republished to retry/DLQ infrastructure.

## Outbox rule

A domain write and its outbox record must commit in the **same service database
transaction**.

The shared `OutboxPublisher` deliberately accepts callbacks instead of importing
service ORM models.

That preserves independent service ownership.

## Object storage

All buckets are private.

Learning binary data belongs in S3-compatible object storage, not PostgreSQL
BLOB columns.

Recommended split:

```text
learning-resources   durable application content; no automatic deletion
platform-imports     temporary; short retention
platform-exports     generated exports
report-exports       generated Reporting CSV/files
```

Object metadata/ownership/version records remain in the owning service database.

## Database pooling

Every service has explicit:

```text
DB_POOL_SIZE
DB_MAX_OVERFLOW
DB_POOL_TIMEOUT_SECONDS
DB_POOL_RECYCLE_SECONDS
DB_STATEMENT_TIMEOUT_MS
DB_APPLICATION_NAME
```

`pool_pre_ping` is enabled.

PostgreSQL sessions use UTC.

The total potential connection count across service replicas must stay below the
database server/managed-pool limit.

Do not configure every replica with a 100-connection pool.

## Migrations

Application replicas do not compete to run Alembic migrations at startup in
production.

Deployment order:

```text
migration job
   ↓
service rollout
   ↓
worker rollout
   ↓
smoke checks
```

## Backups

The Sprint includes:

- PostgreSQL custom-format backups
- individual restore
- isolated restore drill
- object-storage backup with SHA-256 manifest
- object-storage restore
- object-storage retention dry run/apply

A successful `pg_dump` alone is not proof of recoverability. Run restore drills.

## Data retention

Retention is deliberately conservative.

Never automatically delete:

- active jobs
- unprocessed outbox rows
- live inbox deduplication within redelivery horizon
- Learning resources whose lifecycle is still represented in Learning Service

Institutional/legal retention rules override engineering defaults.
