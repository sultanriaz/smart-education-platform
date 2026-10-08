# Sprint 21 Alert Runbooks

Use the correlation/trace IDs from the failing request when available.

Do not begin incident response by changing data directly in another service's
database.

## SmartEduServiceDown

1. Confirm whether the target is truly unavailable or only the metrics endpoint.
2. Check container/process state and `/health`.
3. Check `/ready` for dependency failure.
4. Review recent deployment/config changes.
5. Inspect service logs by `service`.
6. If the process is healthy but readiness fails, inspect the named dependency.
7. Restart only after preserving enough evidence to understand repeated crashes.
8. Escalate if more than one critical service is affected.

## SmartEduHighErrorRate

1. Open the service-detail dashboard.
2. Identify which route templates contribute to 5xx responses.
3. Search Loki for the service and time window.
4. Pivot from a representative log `trace_id` to Tempo.
5. Check downstream dependency spans and database waits.
6. Check recent deployments/migrations.
7. Verify error rate by status class; do not treat expected 4xx as server errors.
8. Roll back or mitigate only after identifying the change/failure boundary.

## SmartEduCriticalErrorRate

Follow `SmartEduHighErrorRate`, but treat this as urgent.

Also:

1. Check whether the error budget is burning rapidly.
2. Pause risky deployments.
3. Consider rollback if a recent deployment clearly correlates with failure.
4. Verify that retries are not amplifying load.

## SmartEduGeneralLatencyBudgetExceeded

1. Confirm p95 is elevated for real user routes, not only one diagnostic path.
2. Break down by route and service.
3. Check dependency p95 traces.
4. Check PostgreSQL locks, slow SQL, and pool usage.
5. Check CPU/memory and queue backlog.
6. Compare against Sprint 20 baseline.
7. Scale only if the bottleneck is actually application capacity.

## SmartEduAttendanceLatencyBudgetExceeded

Attendance has the stricter 2-second SRS target.

1. Break down read versus write routes.
2. Inspect lock waits during bulk/finalization operations.
3. Compare query plans with Sprint 20 evidence.
4. Verify Academic dependency latency.
5. Confirm concurrency controls remain enabled.
6. Never remove advisory/row locks merely to make latency look better.

## SmartEduNotificationLagBudgetExceeded

1. Check source-service outbox backlog.
2. Check RabbitMQ queue depth and oldest message.
3. Check Notification consumer throughput/failures.
4. Check database write latency.
5. Check external email provider only if the SLO being measured includes email.
6. Inspect retries/DLQ.
7. Scale workers if consumers are CPU/concurrency-bound and downstream capacity allows.

## SmartEduOutboxBacklog

1. Check `smartedu_outbox_oldest_age_seconds`.
2. Verify publisher workers are running.
3. Check RabbitMQ connectivity and publisher confirms.
4. Check database transaction/lock failures.
5. Inspect recent poison events.
6. Do not delete pending outbox rows as a first response.

## SmartEduOutboxStale

1. Treat as higher urgency than a small backlog.
2. Find the oldest event and its service.
3. Check publisher attempts/errors.
4. Check broker availability.
5. Confirm successful events are being marked published atomically.
6. Replay only through the supported outbox/replay path.

## SmartEduWorkerFailures

1. Group failures by worker/reason.
2. Check whether one message/job repeatedly fails.
3. Verify retry count and DLQ behavior.
4. Inspect trace/correlation IDs.
5. If caused by a dependency outage, avoid manual retries that create a retry storm.
6. Fix or quarantine poison work through the supported workflow.

## RabbitMQQueueBacklog

1. Identify the queue and whether ready or unacked messages dominate.
2. Check consumer count.
3. Check consumer error/retry rate.
4. Check downstream DB/API latency.
5. Check oldest message age, not only message count.
6. Scale consumers only if processing capacity is the bottleneck.
7. Verify DLQ behavior if failures are permanent.

## PostgreSQL saturation

If dashboards/exporters show high connection or lock pressure:

1. Compare current connections to Sprint 20 connection budget.
2. Check pool checkout wait.
3. Check blocked/locking queries.
4. Check long-running transactions.
5. Check slow query plans.
6. Do not increase `max_connections` before understanding memory and workload impact.

## Redis degradation

1. Identify cache versus durable Redis.
2. Check latency, memory, evictions, and connections.
3. Cache Redis loss should degrade performance but not correctness.
4. Durable Redis loss can affect idempotency/auth-security and requires fail-closed behavior where designed.
5. Do not silently fall back to process-local correctness state.

## Trace collector unavailable

Application correctness must continue if the OTel Collector is temporarily
unavailable.

1. Confirm service request behavior remains normal.
2. Check exporter/collector errors.
3. Check collector memory/queue pressure.
4. Restore collector before increasing sampling.
5. Do not make business requests depend synchronously on trace export.
