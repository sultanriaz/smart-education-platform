# Sprint 23 Integration Checklist

Sprint 23 assumes Sprints 1–22 are merged and green.

## 1. Install deployment toolkit

```powershell
python -m pip install -e .\libs\python\smartedu_deploy
```

Run:

```powershell
.\scripts\run-sprint23.ps1
```

## 2. Reconcile component/runtime ports

Inspect the real Sprint 11 Gateway and Sprint 18 frontend runtime ports.

Generated candidate:

```text
FastAPI services: 8000
frontend:         8080
api-gateway:      8080
```

If the final images use different internal ports, update:

```text
production-topology.yaml
Deployments
Services
Ingress
probes
```

together.

## 3. Reconcile health/readiness routes

FastAPI services assume:

```text
/health
/ready
```

Frontend uses `/`.

Gateway assumes `/health` and `/ready`.

Preserve the actual proven routes if they differ.

## 4. Reconcile runtime configuration

Inspect every service `Settings` class.

Update `smartedu-runtime-config` with real non-secret variable names.

Do not add secrets to ConfigMap.

## 5. Reconcile per-service secrets

Read:

```text
SECRETS_AND_CONFIGURATION.md
deploy/kubernetes/production/secrets.example.yaml
```

Generate the exact secret key list from the real code.

Create one Secret source per workload in the deployment secret manager.

Do not commit real Secret YAML.

## 6. Identity/JWKS

Ensure all downstream services use the actual Identity JWKS/issuer/audience
contract already proven in earlier sprints.

Do not introduce a second signing/trust system for Kubernetes.

## 7. Stateful dependencies

Decide the concrete staging/production products for:

```text
PostgreSQL
Redis cache
Redis durable
RabbitMQ
object storage
email
observability
```

Keep them private.

Preserve database-per-service accounts and least privilege.

## 8. PostgreSQL

Provision all ten service databases/accounts.

Configure:

```text
TLS/private connectivity
HA/failover
PITR/WAL
backups
monitoring
connection limits
```

Recalculate Sprint 20 connection budget against HPA maximum replicas.

## 9. Redis

Provision cache and durable reliability classes separately.

Do not collapse them into one unprotected single-node instance for production.

## 10. RabbitMQ

Use HA broker topology and the Sprint 17 queue/exchange design.

Enable the Sprint 21 metrics endpoint internally.

## 11. Object storage

Provision private buckets and least-privilege credentials for Learning,
Platform, Reporting, and any other actual owner.

Enable versioning/encryption/lifecycle.

## 12. Kubernetes cluster

Production/staging cluster requirements:

```text
multiple worker nodes
Ingress controller
metrics-server for HPA
Pod Security Admission
network policy capable CNI
persistent control-plane/provider backup
private connectivity to stateful services
```

Do not treat a one-node developer Kubernetes cluster as production evidence.

## 13. Ingress

Install/identify the real ingress controller.

Update:

```text
ingressClassName
ingress-controller namespace selector
public hostname
TLS secret
body/time-out annotations
```

Preserve Sprint 18/11 Gateway security behavior.

## 14. DNS

Replace:

```text
smartedu.example.edu
```

with the institution-approved domain.

Then run:

```powershell
python .\scripts\preflight-production.py --strict
```

The placeholder must not survive a production release.

## 15. TLS

Choose:

```text
managed certificate
or
cert-manager
```

If using cert-manager, reconcile the example Certificate and real ClusterIssuer.

Enable Sprint 18 HSTS only after the HTTPS path is proven.

## 16. Network policies

Keep default-deny ingress.

Verify:

```text
Ingress -> frontend/API Gateway
app -> app internal service calls
```

Before go-live, implement provider-specific egress allowlists and then enable
default-deny egress.

Run all distributed integration tests afterward.

## 17. Images

Use Sprint 22's:

```text
release-manifest.json
```

Render:

```powershell
python .\scripts\render-k8s-release.py `
    .\release-manifest.json `
    --output .\deploy\kubernetes\rendered-production.yaml
```

Verify:

```powershell
python .\scripts\verify-k8s-bundle.py `
    .\deploy\kubernetes\rendered-production.yaml
```

Every Deployment image must use `@sha256:`.

## 18. Image signatures

Before deployment, verify Sprint 22 Cosign signatures/attestations.

Do not let the Kubernetes renderer become an alternate unsigned release path.

## 19. HPA/resource tuning

Use Sprint 20 staging evidence to tune:

```text
replicas
min/max replicas
CPU target
memory target
requests
limits
```

Run the 500-user acceptance load after changes.

## 20. Database pools

For each HPA maximum replica count, recompute:

```text
replicas × (pool_size + max_overflow)
```

against the physical database connection limit.

## 21. Observability

Point OTLP to the actual Sprint 21 collector/backend.

Prometheus must scrape internal service metrics.

Observability failure must not block application readiness.

## 22. Backups

Implement `BACKUP_RESTORE_ARCHITECTURE.md`.

At minimum staging must prove:

```text
PostgreSQL restore/PITR
object-version recovery
release redeploy
secret recovery
```

Record elapsed recovery time.

## 23. Pod security

Verify every deployed pod is:

```text
non-root
read-only root filesystem
no privilege escalation
capabilities dropped
seccomp RuntimeDefault
no unnecessary service-account token
```

Fix image compatibility rather than weakening all pods globally.

## 24. Availability behavior

Drain/terminate one application pod.

Confirm:

```text
traffic remains available
readiness removes terminating/unhealthy pod
replacement pod becomes ready
```

Then drain a worker node in staging and confirm disruption budgets behave as
expected.

## 25. Rolling release

Deploy a candidate release and verify:

```text
maxUnavailable=0
new pods ready before old replicas disappear
no 5xx spike beyond accepted budget
```

## 26. Secret rotation rehearsal

Rotate at least one non-production:

```text
database credential
RabbitMQ credential
internal service token
```

without committing the new value to Git.

## 27. Deployment CI

Merge:

```text
.github/workflows/deployment-architecture.yml
```

with Sprint 22 CI.

Keep manifest/toolkit validation on pull requests.

Do not give PR workflows cluster credentials.

## 28. Strict production preflight

Before production readiness:

```powershell
python .\scripts\preflight-production.py `
    --release-manifest .\release-manifest.json `
    --strict
```

It must pass without placeholder DNS.

## 29. Full regression

After deployment reconciliation run:

```text
Sprint 18 security
Sprint 19 QA/E2E
Sprint 20 performance
Sprint 21 observability
Sprint 22 release verification
all ten service suites
frontend
Gateway
```

## 30. Definition of done

Sprint 23 is integrated only when:

- final ports/routes match real images
- real domain replaces placeholder
- TLS strategy is selected
- all 12 workloads render with digest images
- all internal services remain private
- minimum two replicas are deployable
- HPA/PDB/probes work
- stateful dependencies are HA/private
- real per-service secrets are provided from secret storage
- DB connection budget fits max replica counts
- backup/restore design is implemented in staging
- ingress/network policy is tested
- Pod Security baseline passes
- deployment architecture CI passes
- Sprint 18–22 regression remains green
