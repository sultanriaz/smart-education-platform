# Production Launch Monitoring

The first minutes after deployment are an explicit launch phase, not ordinary
background monitoring.

## Intensive window

Default candidate:

```text
first 30 minutes
```

Watch continuously:

```text
HTTP 5xx rate
p95/p99 request latency
Attendance p95
Notification end-to-end/event latency
PostgreSQL connections
PostgreSQL lock waits
Redis health
RabbitMQ ready/unacked queues
DLQ growth
outbox backlog
pod restarts
OOMKilled/throttling
critical alerts
```

## Extended window

Continue heightened review for approximately:

```text
2 hours
```

or longer if institutional launch policy requires it.

## Evidence snapshots

`production-monitoring-snapshot.ps1` records:

```text
Deployments
Pods
Jobs
HPAs
PDBs
Ingress
recent Kubernetes events
```

It deliberately does not dump Secrets or environment variables.

## Alert behavior

Any critical launch alert must be:

```text
acknowledged
assigned
assessed against abort criteria
recorded in the launch incident record if relevant
```

Do not silence an unknown critical alert merely to obtain a successful launch
record.

## Finalization

Before setting outcome `SUCCEEDED`, confirm there is no open SEV-1 launch
incident and all required post-deployment validation phases pass.
