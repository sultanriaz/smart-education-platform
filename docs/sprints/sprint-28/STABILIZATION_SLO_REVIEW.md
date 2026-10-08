# Production SLO and Performance Review

Sprint 28 validates that production behavior remains aligned with the project's
known non-functional targets.

## General latency

Known project target:

```text
95% of normal pages/interactions <= 3 seconds
```

Use production measurements that reflect actual user traffic and representative
Gateway/service paths.

Do not claim the target from one synthetic request.

## Attendance latency

Known target:

```text
Attendance operation <= 2 seconds
```

Review representative production Attendance requests and relevant server-side
latency.

If browser/network time and backend time differ materially, report both.

## Notification latency

Known target:

```text
Notification <= 5 seconds
```

For event-driven delivery measure end-to-end time where possible:

```text
domain event/outbox
RabbitMQ publish
consumer
notification persistence
user-visible availability
```

Do not report only HTTP enqueue time as delivery latency.

## Capacity

Sprint 20 established the controlled load-test evidence.

Sprint 28 asks whether real production utilization invalidates any assumptions:

```text
HPA headroom
DB connection headroom
CPU/memory saturation
RabbitMQ throughput
Redis connections/memory
object-storage latency
```

A low-traffic launch does not re-prove 500-user capacity; it confirms there is
no new production bottleneck contradicting the earlier evidence.

## Availability

Review Sprint 21 SLO/error-budget evidence.

Known target:

```text
>= 99% availability
```

A short stabilization window cannot by itself prove a long-term availability
percentage. Report the observed window separately from the contractual/project
target.

## Closure

Any sustained SRS-level performance regression should become a stabilization
issue and block closure at the appropriate severity.
