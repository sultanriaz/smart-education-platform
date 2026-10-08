# Sprint 21 SLOs and Error Budgets

The source SRS requires:

```text
platform uptime >= 99%
95% of normal pages <= 3 seconds
Attendance operations <= 2 seconds
Notification delivery <= 5 seconds
```

Sprint 21 translates those requirements into operational SLOs.

## Availability

Platform/API availability target:

```text
99.0% over a rolling 30-day window
```

30-day error budget:

```text
1.0% = approximately 7h 12m unavailable time
```

Service-level availability is measured with successful request behavior and
synthetic/health monitoring. A process being alive is not sufficient if the
service cannot serve its intended API.

## General request latency

Target:

```text
95% of representative user-facing requests <= 3 seconds
```

Measure at Gateway/application level and keep browser page timing separate.

## Attendance latency

Target:

```text
95% of Attendance reads/writes <= 2 seconds
```

Do not dilute this SLO by mixing it with `/health`, `/ready`, or `/metrics`.

## Notification latency

Target:

```text
95% of representative notification events visible to the recipient <= 5 seconds
```

This is an end-to-end event SLO:

```text
source transaction
→ outbox
→ RabbitMQ
→ Notification consumer
→ notification persistence
→ recipient-visible state
```

## Error budget policy

When the 30-day availability error budget is:

```text
>50% remaining  normal feature/deployment cadence
25-50%          prioritize reliability work
<25%            freeze non-essential risky changes
exhausted       reliability/incident work only until recovery plan is approved
```

This policy is a project operating model and can be adjusted by the deployment
owner, but changing the original 99% SRS target requires an explicit
requirements decision.

## Burn-rate alerts

The included baseline alert rules focus on immediate symptoms.

During production rollout, add multi-window burn-rate alerts from the finalized
request SLI once traffic patterns and maintenance exclusions are confirmed.

Avoid declaring planned maintenance "successful availability" merely to improve
the number.
