# Sprint 20 Worker Throughput & Scaling

API replicas and background workers should scale independently.

## Notification workers

Measure:

```text
events consumed/sec
email attempts/sec
retry rate
DLQ growth
queue depth
oldest-message age
```

Scale workers when backlog/age grows while downstream provider capacity remains
healthy.

Do not increase concurrency past provider rate limits.

## Reporting projections

Measure:

```text
event ingest/sec
projection update/sec
queue lag
duplicate/redelivery rate
transaction time
```

Reporting should query its own read model, not fan out synchronously to every
service for each dashboard request.

## Outbox publishers

Measure:

```text
pending outbox rows
oldest unpublished age
claimed rows/sec
publish confirms/sec
failure/retry count
```

Scale publishers only after confirming row-claiming is safe across processes.

## File/import jobs

Large imports/exports should run outside API request workers.

Bound:

```text
file size
rows/job
job concurrency
memory per worker
temporary disk
external storage bandwidth
```

## Scale signal

CPU alone is not enough.

Use a combination of:

```text
CPU
request concurrency
p95 latency
DB pool wait
queue depth
queue age
worker throughput
error rate
```

The concrete autoscaling mechanism belongs to deployment Sprints 22–23, but
Sprint 20 supplies the measurements and capacity evidence.
