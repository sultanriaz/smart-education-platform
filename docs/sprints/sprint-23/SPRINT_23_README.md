# Sprint 23 — Deployment Architecture

Sprint 23 defines the final provider-neutral application deployment architecture
for the Smart Education Platform.

The production application target is:

```text
Kubernetes
+ public TLS Ingress
+ private ClusterIP domain services
+ digest-pinned Sprint 22 images
+ external HA stateful dependencies
```

## Production application workloads

Twelve workloads are modeled:

```text
Identity
Academic
Attendance
Scheduling
Notification
Facility
Learning
Assessment
Reporting
Platform
Frontend
API Gateway
```

All start with at least two replicas.

Academic, Attendance, and Assessment start with three replicas based on the
Sprint 20 candidate scaling model.

## Kubernetes controls

Every application workload includes:

```text
RollingUpdate
startup/readiness/liveness probes
resource requests and limits
HorizontalPodAutoscaler
PodDisruptionBudget
topology spreading
preferred anti-affinity
runAsNonRoot
seccomp RuntimeDefault
read-only root filesystem
all Linux capabilities dropped
service-account token automount disabled
```

## Public exposure

Only one Ingress is public.

Routes:

```text
/      -> frontend
/api   -> api-gateway
```

Every Kubernetes Service is `ClusterIP`.

The domain services never receive public `LoadBalancer` Services.

## Stateful architecture

Production PostgreSQL, Redis, RabbitMQ, object storage, and observability are
modeled as external HA dependencies.

The recommendation is managed infrastructure where available, otherwise
dedicated HA clusters outside the app namespace.

The existing database-per-service ownership model remains unchanged.

## Sprint 22 integration

Sprint 22 releases are immutable and digest-pinned.

Sprint 23 does not deploy tag-only images.

Use:

```powershell
python .\scripts\render-k8s-release.py `
    .\release-manifest.json `
    --output .\deploy\kubernetes\rendered-production.yaml

python .\scripts\verify-k8s-bundle.py `
    .\deploy\kubernetes\rendered-production.yaml
```

## Deployment toolkit

New package:

```text
libs/python/smartedu_deploy
```

It validates:

```text
production topology
release manifests
digest-pinned image references
production bundle rendering
```

## Key architecture documents

```text
DEPLOYMENT_ARCHITECTURE.md
PRODUCTION_TOPOLOGY.md
STATEFUL_INFRASTRUCTURE.md
NETWORK_AND_FIREWALL.md
DNS_TLS_FIREWALL.md
SECRETS_AND_CONFIGURATION.md
BACKUP_RESTORE_ARCHITECTURE.md
DISASTER_RECOVERY.md
KUBERNETES_SECURITY.md
CAPACITY_AND_SCALING.md
```

## Important boundary

Sprint 23 defines the target architecture and production manifests.

It does not claim that a real Kubernetes cluster, DNS zone, TLS certificate,
managed PostgreSQL service, or production secret manager has already been
created.

Sprint 24 will instantiate and validate a staging environment from this design.
