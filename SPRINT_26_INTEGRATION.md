# Sprint 26 Integration Checklist

Sprint 26 assumes Sprints 1–25 are merged.

## 1. Install toolkit

```powershell
python -m pip install -e .\libs\python\smartedu_readiness
```

Run:

```powershell
.\scripts\run-sprint26.ps1
```

## 2. Reconcile final accepted release

Identify the exact Sprint 22 release manifest accepted by Sprint 25 UAT.

Record:

```text
release tag
commit SHA
12 image digests
```

Run:

```powershell
python .\scripts\compare-release-manifests.py `
    <uat-accepted-release> `
    <production-candidate-release>
```

There must be an exact match.

## 3. Reconcile real UAT evidence

Use the final Sprint 25 structured UAT run.

Confirm:

```text
run complete
P0 PASS
P1 PASS
pass rate gate PASS
0 BLOCKER
0 CRITICAL
0 MAJOR
five sign-offs
```

Mark `PR-UAT-*` checks PASS only from real evidence.

## 4. Reconcile actual production hostname

Replace any remaining placeholder:

```text
smartedu.example.edu
```

in Sprint 23 production topology/manifests.

Production readiness must fail while a placeholder hostname remains.

## 5. DNS

Verify:

```text
correct hostname
correct load-balancer target
expected TTL
no staging endpoint
ownership/change process
```

Capture evidence for `PR-INF-003`.

## 6. TLS

Verify:

```text
trusted chain
correct hostname
renewal
expiry monitoring
HTTP -> HTTPS
minimum TLS policy
```

Capture evidence for `PR-INF-004`.

## 7. Kubernetes

Validate the real production cluster:

```text
multiple nodes/HA as designed
Ingress controller
metrics-server
network-policy support
Pod Security Admission
production namespace
```

Run Sprint 23 production bundle verification.

## 8. Public exposure

Confirm only:

```text
frontend
api-gateway
```

are routed publicly.

Backend APIs, DB, Redis, RabbitMQ, metrics/admin surfaces stay private.

## 9. Pod security

Verify actual deployed/rendered workloads retain:

```text
runAsNonRoot
RuntimeDefault seccomp
readOnlyRootFilesystem
allowPrivilegeEscalation=false
capabilities drop ALL
no unnecessary service-account token
```

## 10. Production PostgreSQL

Verify:

```text
10 service DBs
10 least-privilege service identities
private/TLS connection
HA/failover
PITR/backups
connection limits
monitoring
```

Prove services cannot query other service DBs.

## 11. Database restore

Reference the latest successful Sprint 24 restore drill.

If the chosen production provider differs materially from staging, perform an
appropriate production-like restore rehearsal before GO.

Record actual achievable RTO/RPO.

## 12. Redis

Verify:

```text
cache tier
durable tier
authentication/ACL
private networking
persistence/recovery for durable tier
```

## 13. RabbitMQ

Verify:

```text
HA topology
durable/quorum queues where required
retry/DLQ
private access
metrics
staging-proven event flows
```

## 14. Object storage

Verify:

```text
private buckets
versioning
encryption
lifecycle
least privilege
restore procedure
```

## 15. Secrets

Inspect actual production secret inventory.

No real secrets in:

```text
Git
container image layers
CI artifacts
readiness evidence
logs
```

Confirm rotation for all critical credential classes.

## 16. Identity keys

Verify production:

```text
JWT signing/verification keys
JWKS publication
key rotation
password reset/security secrets
```

without changing the proven downstream trust contract.

## 17. Security evidence

Rerun/confirm current Sprint 18 evidence for the exact candidate:

```text
auth/RBAC
secret scan
dependency/container scan
upload protections
Origin/cookie controls
least privilege
```

## 18. Supply chain

Verify Sprint 22:

```text
checksum
SBOM
provenance
Cosign signature
registry digest
```

for all 12 images.

## 19. Performance

Confirm the latest accepted evidence covers:

```text
general p95 <=3s
Attendance p95 <=2s
Notification p95 <=5s
>=500 concurrent users
```

Do not claim a smoke profile proves 500-user capacity.

## 20. HPA/DB connection budget

Recompute using production max replicas.

Verify:

```text
sum(max replicas × per-pod DB connections)
```

cannot exhaust physical DB limits under normal scaling.

## 21. Availability/SLO

Confirm Sprint 21:

```text
99% availability target
recording rules/dashboard
alert ownership
```

## 22. Observability

Confirm production or approved managed equivalents for:

```text
metrics
logs
traces
alerts
critical alert delivery
runbooks
```

Observability still must not become a synchronous application dependency.

## 23. Operations ownership

Map generated roles to actual named owners.

Record primary and backup coverage for launch.

## 24. Incident response

Review:

```text
INCIDENT_RESPONSE_HANDOFF.md
Sprint 21 runbooks
```

Ensure launch incident lead and escalation route are known.

## 25. Change freeze

Activate `CHANGE_FREEZE_POLICY.md`.

A code/image change after UAT creates a new release candidate.

## 26. Migration plan

Read:

```text
MIGRATION_PRODUCTION_RUNBOOK.md
```

For every migration-bearing service record:

```text
DB target
owner
duration expectation
lock risk
backup checkpoint
abort threshold
forward-fix strategy
```

## 27. Rollback/abort

Read:

```text
ROLLBACK_AND_ABORT_CRITERIA.md
```

Confirm:

```text
abort authority
schema compatibility
previous digest-pinned release
forward-fix/restore path
```

No automatic production DB downgrade.

## 28. Backup/DR

Complete:

```text
DR_RTO_RPO_DECISION.md
```

Do not state recovery targets that the provider/drills cannot demonstrate.

Unmet high-impact gaps become readiness risks.

## 29. Production data bootstrap

Review:

```text
PRODUCTION_DATA_BOOTSTRAP.md
```

Do not seed Sprint 24 QA data into production.

Any real academic data import requires owner/validation/dry run.

## 30. Launch communications

Complete:

```text
LAUNCH_COMMUNICATIONS.md
```

Record maintenance/user impact/support channel.

## 31. Production surface

When DNS/TLS exists:

```powershell
python .\scripts\check-production-surface.py `
    --url https://<production-host>
```

Reconcile the Gateway path if needed.

## 32. Readiness run

Initialize a run and record each check only from actual evidence.

Do not mass-mark checks PASS without review.

## 33. Risks

Record every unresolved readiness risk.

Default gate permits no open:

```text
BLOCKER
CRITICAL
HIGH
```

MEDIUM/LOW risks still require ownership and mitigation/acceptance.

## 34. Approvals

Record real decisions for:

```text
TechnicalLead
OperationsOwner
SecurityOwner
ProductOwner
ProjectSupervisor
```

CI cannot fabricate approvals.

## 35. Go/no-go

Use:

```text
GO_NO_GO_PROCESS.md
```

Record:

```text
GO
GO_WITH_CONDITIONS
NO_GO
```

`NO_GO` fails the machine gate.

## 36. Evidence index

Place non-secret readiness evidence under:

```text
readiness/evidence/<run-id>/
```

Generate SHA-256 evidence index.

## 37. Final report

Generate:

```text
PRODUCTION_READINESS_REPORT.generated.md
```

Check it matches structured run JSON.

## 38. Sprint 27 handoff

Read:

```text
SPRINT_27_HANDOFF.md
```

Hand off the exact approved immutable release, runbook, evidence, risks, and
decision.

## 39. Definition of done

Sprint 26 is done only when:

- Sprint 25 UAT gate genuinely passed
- real production DNS/TLS is ready
- production bundle has exact accepted digests
- all infrastructure/stateful dependencies are ready
- security/supply-chain gates pass
- 500-user/performance evidence is acceptable
- observability/critical alerts are ready
- restore/DR evidence is acceptable
- migration/rollback/abort plans are complete
- operations/support owners are assigned
- all 59 mandatory checks PASS
- no open BLOCKER/CRITICAL/HIGH risk
- five approvals recorded
- final decision is GO or GO_WITH_CONDITIONS
- evidence/report are archived
- Sprint 27 receives the exact release identity
