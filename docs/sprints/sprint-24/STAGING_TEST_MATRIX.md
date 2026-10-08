# Sprint 24 Staging Test Matrix

## Environment and edge

```text
DNS resolves staging host
TLS hostname/chain valid
HTTP redirects to HTTPS
frontend loads
Gateway route works
domain services are not publicly routable
metrics/internal routes remain private
```

## Kubernetes

```text
12 Deployments Available
12 ClusterIP Services
12 HPAs
12 PDBs
startup/readiness/liveness probes healthy
Pod Security baseline
no bootstrap images
all images digest pinned
```

## Migrations

For every release migration component:

```text
Job uses release digest
Job uses own DB credentials
Job succeeds
Alembic current == head
no second head
```

## Identity/security

```text
login
refresh rotation
HttpOnly cookie
Origin checks
lockout
reset/verification
RBAC
JWKS
logout/session revocation
```

## Academic / Attendance / Scheduling

```text
enrollment/roster
Teacher assignments
attendance create/mark/finalize/correction
schedule recurrence/conflicts
multi-replica concurrency
```

## Learning / Assessment / Facility

```text
private resource access
upload security
resource publish/versioning
quiz/assignment/attempt/grading
answer-key protection
facility booking/conflict
```

## Messaging

```text
transactional outbox
RabbitMQ publish/consume
inbox dedup
retry
DLQ
replay
consumer restart
```

## Reporting / Platform

```text
event projections
dashboard data
CSV/export
audit/job/search/support paths
```

## E2E

```text
Student PASS
Teacher PASS
Admin PASS
```

## Observability

```text
10/10 service metrics
Gateway metrics
logs
HTTP traces
RabbitMQ event traces
alerts
no critical unresolved alert
```

## Performance

```text
Sprint 20 smoke per release
latest baseline recorded
500-user acceptance before production-readiness gate
```

## Resilience

```text
pod deletion recovery
rolling update
node drain where multi-node
dependency outage behavior
```

## Recovery

```text
PostgreSQL isolated restore
object restore/checksum
release redeploy
secret recovery
credential rotation
```

## Promotion

All mandatory rows must be PASS or have an approved, explicit, time-bounded
exception. A skipped mandatory test is not a PASS.
