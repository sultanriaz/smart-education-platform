# Stateful Infrastructure Architecture

Production application pods remain stateless wherever possible.

## PostgreSQL

Preferred:

```text
managed HA PostgreSQL with multi-zone failover
```

Alternative:

```text
dedicated HA PostgreSQL cluster operated outside the app namespace
```

Keep the existing database-per-service ownership model:

```text
identity_db
academic_db
attendance_db
scheduling_db
notification_db
facility_db
learning_db
assessment_db
reporting_db
platform_db
```

Service accounts retain access only to their own databases.

Use connection encryption and private network endpoints.

## Redis

Keep two logical reliability classes:

```text
redis-cache
redis-durable
```

`redis-cache` is disposable acceleration state.

`redis-durable` supports correctness-sensitive distributed state such as
idempotency/security coordination and must use HA/persistence appropriate to the
final Redis product.

A cache failure may hurt performance but must not change source-of-truth data.

## RabbitMQ

Production should use a highly available RabbitMQ deployment/service.

Use durable queues and quorum queues where the existing Sprint 17 design
requires them.

Transactional outboxes remain the source-side reliability mechanism. RabbitMQ
must not become the only copy of a business state transition.

## Object storage

Prefer an S3-compatible managed object store with:

```text
private buckets
versioning
server-side encryption
lifecycle policy
least-privilege per-service credentials
```

Do not expose MinIO administrative credentials to application pods.

## Email

Email is an external delivery dependency.

Notification persistence remains internal even if email delivery is degraded.

Use provider credentials only in Notification Service.

## Observability

For production, decide in Sprint 26 whether to use:

```text
managed telemetry backend
or
HA persistent Prometheus/Loki/Tempo/Grafana equivalents
```

The Sprint 21 single-node reference stack is suitable for development/staging,
not a final HA guarantee.
