# Sprint 24 Integration Checklist

Sprint 24 assumes Sprints 1–23 are merged.

## 1. Install staging toolkit

```powershell
python -m pip install -e .\libs\python\smartedu_staging
```

Run the offline checks:

```powershell
.\scripts\run-sprint24.ps1
```

## 2. Reconcile Sprint 23 manifests

Inspect actual:

```text
container ports
health/readiness routes
writable filesystem needs
runtime environment variables
```

Update staging manifests in parallel with production if the actual images
differ from the generated candidate.

Staging must not drift into a separate architecture.

## 3. Real staging hostname

Replace:

```text
staging.smartedu.example.edu
```

with the approved staging DNS hostname.

Then run:

```powershell
python .\scripts\staging-preflight.py --strict
```

Placeholder domains must fail strict mode.

## 4. TLS

Provision the staging certificate using the same mechanism intended for
production where possible.

Verify:

```text
hostname
certificate chain
expiry/renewal
HTTPS redirect
```

## 5. Staging cluster

The staging cluster needs:

```text
multiple worker nodes where possible
Ingress controller
metrics-server
network-policy capable CNI
Pod Security Admission
access to private staging dependencies
```

A one-node local cluster can be used for developer smoke but does not satisfy
the failure-drill acceptance gate.

## 6. Stateful dependencies

Choose/provision staging:

```text
PostgreSQL
redis-cache
redis-durable
RabbitMQ
object storage
email sandbox
observability
```

Use `config/staging/dependencies.yaml` as the contract.

Do not point any staging service to production endpoints.

## 7. Ten service databases

Create:

```text
identity_db
academic_db
attendance_db
scheduling_db
notification_db
facility_db
learning_db
assessment_db
reporting_db
platform_db
```

with separate service accounts.

No cross-service database privileges.

## 8. Secret contract

Inspect the real settings classes.

Reconcile `secrets.example.yaml`.

Create the 12 required Kubernetes Secrets from staging secret storage.

Do not apply `secrets.example.yaml`.

Run:

```powershell
python .\scripts\staging-secret-check.py
```

## 9. QA identities

Create dedicated staging:

```text
Student
Teacher
Admin
```

users.

Use CI/staging environment secret storage for passwords.

Do not use production accounts.

## 10. QA fixtures

Reconcile:

```text
config/staging/fixture-plan.yaml
```

with actual APIs.

Implement or reuse an idempotent API-driven seeder.

Do not seed by writing another service's database.

## 11. Release manifest

Use an actual Sprint 22 release.

Verify checksum/Cosign/attestation before deployment.

The same release manifest must supply all 12 images.

## 12. Render staging bundle

```powershell
python .\scripts\render-staging-release.py `
    .\release-manifest.json `
    --output .\deploy\kubernetes\rendered-staging.yaml
```

Then:

```powershell
python .\scripts\verify-staging-bundle.py `
    .\deploy\kubernetes\rendered-staging.yaml
```

There must be no bootstrap/tag-only images.

## 13. Migrations

Only `migration_components` from the release should create migration Jobs.

Verify each:

```text
uses exact release digest
has only its own DATABASE_URL
completes exactly once for deployment attempt
leaves schema at Alembic head
```

Migration failure blocks rollout.

## 14. Deploy application

Use:

```powershell
.\scripts\deploy-staging-k8s.ps1 `
    -ReleaseManifest .\release-manifest.json
```

Confirm all 12 Deployment rollouts.

## 15. Public smoke route

Reconcile the real Gateway health/smoke route.

The generated `staging-public-smoke.py` defaults to:

```text
/api/health
```

only as an integration baseline.

If the actual Gateway does not publicly expose that path, configure a known
safe public path instead.

Do not expose service-internal `/metrics` or `/internal`.

## 16. Sprint 19 live QA

Run live:

```text
contract tests
authorization matrix
migration checks
event reliability
failure behavior
Student E2E
Teacher E2E
Admin E2E
```

No required gate may be silently skipped.

## 17. Event flows

Verify representative:

```text
Attendance -> Reporting
Assessment -> Reporting
domain event -> Notification
RabbitMQ retry -> DLQ -> replay
```

against the staging broker.

## 18. Sprint 20

Run:

```text
smoke on every staging release
baseline periodically
srs-500 before production readiness
```

Do not call staging production-capable based only on the smoke profile.

## 19. Sprint 21

Verify:

```text
10/10 service metrics
Gateway metrics
logs
traces
async event traces
alerts
```

Staging environment labels must be distinct from production.

## 20. Pod failure drill

Run:

```powershell
.\scripts\staging-pod-failure-drill.ps1
```

for at least:

```text
api-gateway
attendance-service
assessment-service
```

Confirm recovery and no unacceptable user outage.

## 21. Rolling update drill

Run:

```powershell
.\scripts\staging-rolling-update-drill.ps1
```

Verify `maxUnavailable=0` works in practice.

## 22. Node drain

On a multi-node staging cluster:

```powershell
.\scripts\staging-node-failure-drill.ps1 `
    -Confirm STAGING_ONLY
```

Review PDB behavior.

Do not run this against production.

## 23. PostgreSQL recovery drill

Configure provider-specific scripts:

```text
STAGING_DB_BACKUP_SCRIPT
STAGING_DB_RESTORE_SCRIPT
STAGING_DB_VERIFY_RESTORE_SCRIPT
```

Then execute the isolated restore drill.

Record elapsed recovery time.

## 24. Object-storage recovery drill

Configure:

```text
STAGING_OBJECT_BACKUP_SCRIPT
STAGING_OBJECT_RESTORE_SCRIPT
STAGING_OBJECT_VERIFY_RESTORE_SCRIPT
```

Verify restored object content/checksum and private access.

## 25. Secret rotation

Rotate at least one staging credential.

Verify application recovery/restart behavior.

Do not recover the value from Git.

## 26. Network policies

Verify:

```text
only Ingress -> frontend/Gateway publicly
internal service communication works
direct public domain-service access fails
```

If enabling Sprint 23 default-deny egress, complete every dependency egress rule
first.

## 27. Security

Run Sprint 18 regression against staging.

Also verify:

```text
no production credentials
no public databases/brokers/Redis
no public metrics/internal APIs
TLS enabled
```

## 28. Staging workflow

Reconcile:

```text
.github/workflows/staging-environment.yml
```

with existing Sprint 22 staging workflow.

Prefer one canonical staging deployment path after merge rather than two
competing workflows.

Environment approval remains required.

## 29. Evidence

Keep release-specific staging artifacts:

```text
release manifest
Kubernetes state
migration results
JUnit
Playwright report
performance output
observability checks
recovery drill evidence
```

Never upload secrets.

## 30. Promotion

Read:

```text
STAGING_PROMOTION_GATE.md
```

Only promote the exact digest-pinned release tested here.

## 31. Definition of done

Sprint 24 is complete when:

- real staging DNS/TLS works
- stateful staging dependencies exist
- no staging dependency points to production
- all 12 workloads deploy from immutable release digests
- all required migrations succeed
- deterministic QA data exists
- Student/Teacher/Admin E2E pass
- event flows pass
- security checks pass
- performance smoke passes
- observability passes
- pod failure passes
- rolling update passes
- node drain passes where cluster supports it
- database restore drill passes
- object restore drill passes
- staging evidence is archived
- the exact tested release is ready for UAT
