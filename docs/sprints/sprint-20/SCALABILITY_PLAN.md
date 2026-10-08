# Sprint 20 Scalability Plan

## Stateless HTTP services

The FastAPI services should remain horizontally scalable:

```text
Gateway
   ↓
N replicas of service
   ↓
service-owned PostgreSQL / Redis / broker / S3
```

No request should depend on process-local session state for correctness.

Sprint 16 idempotency and Sprint 18 refresh sessions already use shared durable
state where required.

## Candidate replica topology

The included scaling candidate starts with more replicas for the likely
high-traffic Academic, Attendance, and Assessment services.

This is a hypothesis to test, not a production guarantee.

Run at least:

```text
1 replica baseline
candidate replica topology
500-user SRS run
stress run
```

Compare:

```text
throughput
p95/p99
CPU
memory
DB connections
pool wait
broker queue age
error rate
```

## Bottleneck decision tree

If p95 rises:

```text
Check error rate
  ↓
Check service CPU/memory
  ↓
Check DB pool wait
  ↓
Check slow SQL/locks
  ↓
Check Redis/broker/S3 latency
  ↓
Check downstream service fan-out
```

Do not scale application replicas when the real bottleneck is a locked table or
an exhausted database connection budget.

## 500 concurrent users

The SRS requirement is concurrency, not simply "500 requests".

A valid acceptance run must sustain approximately 500 active virtual users with
representative think time and role mix.

Report:

```text
spawn pattern
duration
role distribution
requests/sec
error rate
p50/p95/p99
infrastructure utilization
```
