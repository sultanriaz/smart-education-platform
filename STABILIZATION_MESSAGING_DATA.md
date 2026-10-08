# Messaging and Data Stabilization

## RabbitMQ

Review:

```text
queue ready count
unacked messages
publish/consume rates
consumer count
retry queues
DLQ volume
connection/channel errors
```

A queue can be non-zero and healthy.

The concern is:

```text
unbounded backlog
consumer failure
repeated poison messages
unexpected DLQ growth
```

## Transactional outbox

For outbox-enabled services verify:

```text
pending backlog
oldest pending age
retry/failure count
publisher health
```

A growing outbox may indicate broker failure, publisher failure, or downstream
pressure.

## Inbox/idempotency

Review duplicate-event handling.

There should be no known incident where event retries caused duplicated
business side effects such as:

```text
duplicate notification
duplicate reporting projection
duplicate facility transition
duplicate grading side effect
```

## PostgreSQL

Review:

```text
connections
pool exhaustion
lock waits
deadlocks
long transactions
replication/HA status
storage growth
backup status
```

## Reporting

Use known QA/canary/real events where authorized to confirm event-driven
projections remain consistent.

Do not repair Reporting by directly querying another service database.

## Data integrity

Any suspected corruption or data loss is not a normal stabilization follow-up.

Escalate using the incident/recovery plan.
