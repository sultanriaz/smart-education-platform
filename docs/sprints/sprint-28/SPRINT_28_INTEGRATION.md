# Sprint 28 Integration Checklist

Sprint 28 assumes Sprints 1–27 are merged and a real Sprint 27 production launch
completed successfully.

## 1. Install toolkit

```powershell
python -m pip install -e .\libs\python\smartedu_stabilization
```

Run offline verification:

```powershell
.\scripts\run-sprint28.ps1
```

## 2. Verify Sprint 27 launch

Use the real:

```text
release-manifest.json
launch/current-launch.json
PRODUCTION_LAUNCH_REPORT.md
```

Run stabilization preflight.

Do not open a stabilization run for a failed/rolled-back/aborted launch.

## 3. Verify live immutable images

Run:

```powershell
python .\scripts\verify-live-release-images.py `
    <release-manifest> `
    --context <production-context>
```

All 12 Deployment images must match the release manifest.

Any unexplained drift is a stabilization issue.

## 4. Reconcile checkpoint catalog

Review:

```text
config/stabilization/checkpoints.yaml
```

Map evidence to the real platform/provider/monitoring stack.

Do not remove mandatory checks to simplify closure.

## 5. Observation window

Reconcile:

```text
config/stabilization/windows.yaml
```

with real traffic.

At minimum gather evidence across enough time to observe:

```text
normal Student traffic
normal Teacher traffic
normal Admin/operations traffic
scheduled/async work
backup cycle where practical
```

## 6. General latency

Review production metrics for:

```text
95% normal interaction target <=3 seconds
```

Use real production measurements.

## 7. Attendance latency

Review actual Attendance latency against:

```text
<=2 seconds
```

Record whether measurement is browser end-to-end, Gateway, or backend.

## 8. Notification latency

Measure actual end-to-end delivery/visibility where possible against:

```text
<=5 seconds
```

Do not use enqueue time as a substitute.

## 9. Capacity

Review:

```text
HPA utilization/headroom
DB connections
CPU/memory
RabbitMQ throughput/backlog
Redis memory/connections
```

Do not claim real production traffic alone re-proves 500-user capacity.

Use Sprint 20 as controlled capacity evidence.

## 10. Availability

Review Sprint 21 production SLO data.

Distinguish:

```text
observed stabilization-window availability
project target >=99%
```

## 11. PostgreSQL

Inspect:

```text
connection pool usage
locks
deadlocks
long transactions
storage growth
backup/PITR health
HA/failover status
```

## 12. Redis

Inspect cache and durable Redis separately.

Review:

```text
connections
latency
errors
evictions
memory
persistence/replication
```

according to each tier's purpose.

## 13. RabbitMQ

Inspect:

```text
ready/unacked
publish/consume rates
consumer count
retry queues
DLQ
connection/channel failures
```

A non-zero queue is not automatically unhealthy; look for trend/backlog growth.

## 14. Outbox/inbox

Verify:

```text
outbox backlog drains
oldest pending age is acceptable
retry rate understood
consumer inbox dedup works
no duplicate business side-effect incidents
```

## 15. Reporting/data integrity

Verify event-driven reporting projections remain consistent for selected known
production-safe events.

Never repair reporting through direct cross-service DB queries.

## 16. Production workloads

Confirm all 12 Deployments remain healthy.

Review:

```text
available replicas
restarts
OOM
probe failures
HPA behavior
Kubernetes events
```

## 17. Snapshot automation

Use:

```powershell
.\scripts\production-stabilization-snapshot.ps1
```

This is read-only.

## 18. Observer hooks

Implement/reconcile:

```text
STABILIZATION_METRICS_CHECK_SCRIPT
STABILIZATION_MESSAGING_CHECK_SCRIPT
STABILIZATION_SECURITY_CHECK_SCRIPT
STABILIZATION_SUPPORT_CHECK_SCRIPT
```

These should gather/validate the real platform evidence.

They must not modify production merely to make a checkpoint pass.

## 19. Security review

Read:

```text
STABILIZATION_SECURITY_REVIEW.md
```

Review:

```text
auth anomalies
admin audit
secret exposure
operator access
public surface
JWT/JWKS errors
security alerts
```

## 20. Support queue

Review all launch-period user reports.

Every real issue must be:

```text
triaged
severity-classified
owned
linked to issue/follow-up
```

## 21. Stabilization issues

Use:

```powershell
python .\scripts\record-stabilization-issue.py ...
```

Default closure requires no open SEV-1/SEV-2/SEV-3.

Do not hide a defect as a follow-up.

## 22. Follow-ups

Use follow-ups for bounded residual work after the service is stable.

HIGH follow-ups must be closed before closure.

MEDIUM/LOW follow-ups require clear ownership and target dates.

## 23. Hotfix discipline

Read:

```text
HOTFIX_PROCESS.md
config/stabilization/hotfix-policy.yaml
```

A hotfix must create a new immutable release.

Reuse Sprints 22–27 controls.

## 24. Security hotfix

Require SecurityOwner review for security hotfixes.

Retain:

```text
tests
SBOM
provenance/signature
protected deployment
monitoring
```

## 25. Migration hotfix

Any hotfix migration remains service-owned and release-tracked.

No manual cross-service SQL.

## 26. Operational docs

Review runbooks for current:

```text
hostnames
service names
owner roles
alert destinations
deployment flow
```

Do not place live credentials in docs.

## 27. Backup/recovery ownership

Verify:

```text
backup jobs healthy
restore escalation known
owner/backup owner assigned
```

A failed production backup schedule is not a cosmetic issue.

## 28. Approvals

Record:

```text
TechnicalLead
OperationsOwner
SecurityOwner
ProductOwner
ProjectSupervisor
```

Approvals must come from actual review.

CI does not fabricate them.

## 29. Closure disposition

Allowed:

```text
STABLE
STABLE_WITH_FOLLOWUPS
```

`UNSTABLE` fails closure.

## 30. Generate evidence index

Review evidence for secrets before hashing/archiving.

Generate the SHA-256 evidence index.

## 31. Generate final report

Generate:

```text
PRODUCTION_STABILIZATION_REPORT.md
```

Verify it matches the structured run.

## 32. Support/operations handoff

Read:

```text
SUPPORT_OPERATIONS_HANDOFF.md
```

Operations/support must accept ongoing ownership.

## 33. Final project closure

Read:

```text
FYP_OPERATIONAL_CLOSURE.md
```

Archive:

```text
requirements/traceability
architecture
test/security/performance evidence
UAT
readiness
launch
stabilization
release manifests/evidence indexes
```

Never archive production credentials or private user data.

## 34. Definition of done

Sprint 28 is complete only when:

- Sprint 27 launch was genuinely successful
- live 12-image release identity matches
- all 49 checkpoints PASS
- no open SEV-1
- no open SEV-2
- no open SEV-3
- no open HIGH follow-up
- production SRS latency evidence is acceptable
- DB/Redis/RabbitMQ/outbox health is acceptable
- no unresolved critical security alert
- support issues are triaged
- backups/operations ownership is accepted
- five closure approvals are recorded
- disposition is STABLE or STABLE_WITH_FOLLOWUPS
- final report/evidence index are archived
- FYP transitions to normal operational ownership
