# Sprint 17 Integration Checklist

Sprint 17 assumes Sprints 1–16 are merged.

## 1. Overlay files

Extract Sprint 17 at repository root.

Preserve existing service domain code.

## 2. Build/install shared packages

Sprint 17 depends on Sprint 16 `smartedu-contracts`.

Build Sprint 16 contracts first, then:

```powershell
.\scripts\build-infra-wheel.ps1
.\scripts\install-infra-wheel.ps1
```

For service images follow:

```text
infra/docker/SPRINT_17_DOCKER_PATTERN.md
```

## 3. Start local infrastructure

```powershell
Copy-Item .env.infrastructure.example .env.infrastructure
.\scripts\start-infrastructure.ps1
```

Verify healthy:

```text
infra-postgres
redis-cache
redis-durable
rabbitmq
minio
```

`minio-bootstrap` should exit successfully after bucket creation.

## 4. Database ownership

For each service, reconcile its real `DATABASE_URL`.

Inside Docker:

```text
Identity:
postgresql+psycopg://identity_svc:<secret>@infra-postgres:5432/identity_db

Academic:
postgresql+psycopg://academic_svc:<secret>@infra-postgres:5432/academic_db

...
```

No service receives credentials for another service database.

Search for cross-service database URLs and remove them.

## 5. Migrate existing engine creation

Inspect each service's current SQLAlchemy setup.

Converge on the Sprint 17 bounded pool configuration or equivalent:

- `pool_pre_ping`
- pool size
- max overflow
- pool timeout
- recycle
- PostgreSQL statement timeout
- UTC
- application name

Do not create two Engine objects per process accidentally.

SQLite test engines may keep their test-specific settings.

## 6. Alembic

For every service:

- preserve its existing migration history
- verify one head unless multiple heads are intentional
- `upgrade head`
- schema-drift check
- rollback/down migration where supported

Use:

```powershell
.\scripts\check-migration-heads.ps1
```

and the per-service runner:

```powershell
.\scripts\migrate-service.ps1 -Service academic-service
```

Production migration execution belongs in deployment orchestration, not every
application replica's startup path.

## 7. Seeds

Identify every current seed script.

Classify:

```text
required bootstrap
institution master data
demo-only data
```

Keep production bootstrap seeds idempotent.

Identity RBAC seeding must remain safe to rerun.

Do not mix demo data with production seeds.

## 8. Sprint 16 idempotency Redis

Configure:

```text
IDEMPOTENCY_REDIS_URL=redis://redis-durable:6379/1
```

Do not point correctness-critical idempotency to `redis-cache`.

Test two application replicas against the same durable Redis.

## 9. Cache migration

Inspect service cache usage.

Use `redis-cache` only for disposable derived data.

Every cache entry needs:

- namespace
- bounded TTL
- invalidation/refresh strategy
- no source-of-truth semantics

Do not cache authorization decisions longer than the underlying authorization
state can safely tolerate.

## 10. RabbitMQ topology

Install `smartedu-infra`, configure `RABBITMQ_URL`, then:

```powershell
python .\scripts\bootstrap_rabbitmq.py
```

Verify exchanges:

```text
smartedu.events
smartedu.retry
smartedu.dlx
```

Verify queues for configured consumers.

Review:

```text
contracts/event-subscriptions.json
```

and reconcile subscriptions with actual Sprint 4–16 events.

Do not subscribe Notification/Reporting/Platform to events they do not
understand merely because a wildcard is convenient in production.

The initial wildcard consumers are appropriate only where the consumer has a
generic event/audit ingestion path.

## 11. Existing outbox/inbox systems

Inspect current services, especially:

- Facility
- Notification
- Reporting
- Platform
- Scheduling
- Attendance
- Assessment
- Learning

Preserve existing transactional outbox/inbox tables and race protection.

Adapt their transport to RabbitMQ instead of replacing transactional guarantees.

Business transaction:

```text
domain write + outbox row
```

must commit atomically.

Publisher marks an outbox row published only after RabbitMQ confirms publish.

## 12. Event consumer failure path

Test:

1. valid event succeeds and ACKs
2. handler failure republishes to retry queue
3. retry is delayed
4. attempt header increments
5. success after retry ACKs
6. repeated failure reaches DLQ
7. DLQ replay works after defect is corrected
8. duplicate `event_id` does not repeat business side effects

Do not use immediate `requeue=True` loops.

## 13. Worker processes

Run event consumers as separate worker processes/containers where appropriate.

Do not start multiple independent infinite worker loops from each web request
process.

Use `run_event_worker(...)` with each service's EventRouter.

Web and worker deployments can scale independently.

## 14. Object storage

Migrate Learning's existing S3/MinIO code to the shared ObjectStorage helper or
an equivalent tested client.

Verify:

- private bucket
- allowed file types remain enforced by Learning Service
- max upload size remains enforced
- safe keys
- no `..` traversal
- presigned URLs are short-lived
- unauthorized users cannot access object metadata/download flows
- database contains metadata/key, not binary blob

Review whether Platform imports/exports and Reporting exports should also use
object storage.

## 15. Object backup/restore

With local MinIO credentials exported:

```powershell
python .\scripts\object_storage_backup.py `
  --output .\backups\objects\test

python .\scripts\object_storage_restore.py `
  --input .\backups\objects\test `
  --force
```

Verify checksums.

## 16. Database backup/restore

```powershell
.\scripts\backup-databases.ps1
```

Then restore-drill at least:

```text
identity_db
academic_db
attendance_db
assessment_db
platform_db
```

using:

```powershell
.\scripts\verify-backup-restore.ps1 -BackupFile <file>
```

Before staging/prod release, test all service databases.

## 17. Production backup architecture

For production configure:

- encrypted automated PostgreSQL backups
- off-host storage
- PITR/WAL where available
- object-storage redundancy/versioning
- backup failure alerts
- retention
- periodic restore drills

Document actual RPO/RTO.

## 18. Retention

Review:

```text
contracts/retention-policy.yaml
```

Map real table names.

Never apply the generic SQL retention helper to a table until the exact terminal
state predicate is reviewed.

For temporary object storage:

```powershell
python .\scripts\object_storage_retention.py
```

is dry-run.

Only after review:

```powershell
python .\scripts\object_storage_retention.py --apply
```

## 19. Indexing and query health

Run:

```powershell
.\scripts\db-diagnostics.ps1
```

Inspect:

- slow queries
- large sequential scans
- dead tuples
- unused indexes
- table sizes

Add indexes through each service's Alembic history.

High-priority query/index review:

- Identity email/user/role lookup
- Academic course/semester/section/enrollment/assignment lookup
- Attendance section/session/student summaries
- Scheduling section/Teacher/room/time conflicts
- Notification inbox/unread/delivery/outbox
- Facility availability/booking overlap
- Learning target/resource/version lookup
- Assessment assignment/attempt/student grading lookup
- Reporting projection dimensions/timestamps
- Platform audit/service/job/support search

Do not add every conceivable index; indexes have write/storage cost.

## 20. Environment separation

Validate development, staging, production independently.

Production must not reuse:

- dev database
- dev Redis
- dev RabbitMQ vhost
- dev S3 buckets
- dev credentials
- local default passwords

## 21. Full regression

Run:

```text
smartedu-contracts tests
smartedu-infra tests

Identity
Academic
Attendance
Scheduling
Notification
Facility
Learning
Assessment
Reporting
Platform
Gateway
Frontend

Student E2E
Teacher E2E
Admin E2E
```

## 22. Definition of done

Sprint 17 is complete only when:

- all ten services use owned DB credentials
- bounded connection pools are verified
- Sprint 16 idempotency uses durable Redis in staging/prod
- event transport uses RabbitMQ
- retry/DLQ behavior passes
- existing outbox/inbox guarantees remain intact
- Learning binary storage is S3-compatible
- backups have successful restore drills
- migration execution is serialized
- retention rules are documented/tested
- query/index diagnostics are reviewed
- no infrastructure data port is public in production
- Student/Teacher/Admin E2E remains green
