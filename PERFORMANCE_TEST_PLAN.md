# Sprint 20 Performance Test Plan

## Objectives

Prove that the Smart Education Platform can sustain the original SRS
performance expectations under representative distributed load.

Primary acceptance targets:

```text
>= 500 concurrent users
95% of normal page/API interactions <= 3 seconds
Attendance operations <= 2 seconds
Notification visibility/delivery <= 5 seconds
Error rate <= 1% during steady-state acceptance load
```

These targets must be measured on the merged system, not inferred from unit
tests.

## Workload mix

Default virtual-user distribution:

```text
Student 75%
Teacher 20%
Admin    5%
```

This reflects the expected institutional population shape and prevents a
load test dominated by rare Admin activity.

Action mixes are stored in:

```text
tests/performance/config/workload-mix.yaml
```

Codex should reconcile these percentages with any actual project/demo usage
assumptions before final acceptance.

## Profiles

### Smoke

```text
20 users
5 users/sec spawn
2 minutes
```

Purpose: catch obvious errors before expensive tests.

### Baseline

```text
100 users
10 users/sec spawn
5 minutes
```

Purpose: stable regression reference.

### SRS acceptance

```text
500 users
25 users/sec spawn
10 minutes
```

Purpose: prove the required concurrency target.

### Stress

```text
750 users / 10 minutes
1000 users / 10 minutes
```

Purpose: find saturation/headroom. These are exploratory unless later adopted as
release targets.

### Soak

```text
250 users
30 minutes
```

Purpose: detect:

```text
memory leaks
connection leaks
pool exhaustion
queue buildup
Redis memory growth
slow cache degradation
worker backlog
```

## Authentication behavior

For long tests, Locust users should authenticate with dedicated QA credentials.

The load harness uses the real Sprint 18 browser-compatible model:

```text
login
  ↓
access JWT in memory
refresh token in HttpOnly cookie jar
  ↓
401
  ↓
refresh endpoint
  ↓
rotated refresh cookie + new access JWT
```

Do not issue artificially long-lived access tokens just to make a soak test
easier.

## Read versus mutation load

The default weighted role workload is primarily read-oriented because repeated
random mutations can corrupt deterministic QA fixtures.

Mutation workloads are separate:

```text
AttendanceMutationUser
GenericMutationUser
```

Mutation performance runs require dedicated disposable QA records and an
idempotency-safe request contract.

## Attendance

Attendance has an explicit 2-second target.

Measure separately:

```text
student attendance summary reads
Teacher session/roster reads
bulk mark/update writes
session finalize where relevant
```

The acceptance result should report p50/p95/p99 and error rate.

## Notifications

The SRS notification target is an end-to-end latency target, not merely the
latency of `GET /notifications`.

Use:

```text
scripts/measure-notification-latency.py
```

to measure:

```text
source request accepted
        ↓
outbox
        ↓
RabbitMQ
        ↓
Notification worker
        ↓
recipient inbox becomes visible
```

The target is <=5 seconds for 95% of representative notification events.

## Browser page timing

Sprint 20 adds a Playwright performance smoke spec to the Sprint 19 E2E suite.

It checks role workspace navigation against a 3-second smoke budget.

For final acceptance, run the important role pages repeatedly and publish p95,
rather than relying on one navigation sample.

## Test environment

Performance tests must run against QA/staging with production-like:

```text
PostgreSQL
Redis
RabbitMQ
S3/MinIO or production-equivalent object storage
Gateway
multiple service replicas where candidate scaling is being evaluated
```

Laptop-local results are useful for regressions but are not production capacity
evidence.

## Warm-up

Before measuring:

```text
start all replicas
verify readiness
allow DB pools to establish
warm representative caches if the workload normally sees warm cache
run a short smoke profile
```

Do not mix initialization/migration time into steady-state request percentiles.

Cold-cache behavior should be measured as a separate experiment.

## Observation data

For every serious run capture:

```text
Locust stats/history/failures
service replica counts
service CPU/memory
Gateway errors
PostgreSQL connection count
DB pool wait/exhaustion
slow SQL / pg_stat_statements
lock waits
Redis ops/memory/latency
RabbitMQ queue depth and oldest-message age
worker throughput
S3 latency
```

Sprint 21 will formalize the observability stack. Sprint 20 still requires these
measurements during manual performance runs.

## Pass/fail

The `evaluate-performance.py` script applies endpoint budgets to Locust output.

Acceptance also requires confirming that the run actually sustained the intended
virtual-user count and that infrastructure was healthy.

A low-latency run that silently dropped most users/requests is not a pass.

## Regression comparison

Store a known-good baseline evaluation JSON.

Compare a candidate with:

```powershell
python .\scripts\compare-performance.py `
  .\baseline\evaluation.json `
  .\candidate\evaluation.json
```

Default regression limits:

```text
p95 increase >20% => fail
throughput drop >20% => fail
error rate above baseline and >1% => fail
```

Absolute SRS budgets still take precedence.
