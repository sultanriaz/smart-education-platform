# Sprint 23 Deployment Architecture

Sprint 23 defines the production deployment target for the Smart Education
Platform without tying the system to one cloud vendor.

## Production shape

```text
Internet
   |
HTTPS :443
   |
Managed / HA load balancer
   |
Kubernetes Ingress Controller
   |
   +------------------+
   |                  |
Frontend          API Gateway
                      |
       +--------------+--------------+
       |              |              |
   Identity       Academic       Attendance
   Scheduling     Notification   Facility
   Learning       Assessment     Reporting
   Platform
       |
Private network dependencies
       |
PostgreSQL / Redis / RabbitMQ / Object Storage / Email
```

Only the Ingress load balancer is Internet-facing.

The API Gateway and frontend are Kubernetes `ClusterIP` services behind the
Ingress. All domain services are private `ClusterIP` services.

## Why Kubernetes

The platform already has:

- independently deployable services
- per-service containers
- health/readiness endpoints
- stateless HTTP APIs
- externalized databases
- Redis/RabbitMQ/object storage
- horizontal-scaling requirements
- Sprint 22 immutable release images
- Sprint 21 metrics/tracing

Kubernetes provides a natural production scheduling layer for these properties:

- rolling deployment
- replica scheduling
- service discovery
- health-based traffic removal
- disruption budgets
- autoscaling
- secret/config injection
- network policies
- immutable image deployment

Sprint 23 does not require a specific managed Kubernetes provider.

## Stateless workloads

Production manifests cover 12 deployable workloads:

```text
10 FastAPI domain/platform services
frontend
API Gateway
```

Every workload has:

- at least two replicas
- resource requests/limits
- startup/readiness/liveness probes
- rolling update with zero planned unavailable pods
- HPA
- PodDisruptionBudget
- non-root pod security
- read-only root filesystem
- dropped Linux capabilities
- no service-account token automount
- topology spreading / pod anti-affinity

Replica/resource values are candidate starting points from the Sprint 20
capacity model, not production capacity claims.

## Stateful dependencies

PostgreSQL, Redis, RabbitMQ, object storage, and production observability are
outside the application Kubernetes manifests.

Recommended production mode:

```text
managed service
or
dedicated highly available cluster
```

Do not run production stateful dependencies as single-replica sidecars in the
application namespace.

## Release integration

Sprint 22 produces:

```text
release-manifest.json
```

with digest-pinned images.

Sprint 23 renders those exact images into the production Kubernetes bundle:

```powershell
python .\scripts\render-k8s-release.py `
    .\release-manifest.json `
    --output .\deploy\kubernetes\rendered-production.yaml
```

Then:

```powershell
python .\scripts\verify-k8s-bundle.py `
    .\deploy\kubernetes\rendered-production.yaml
```

The rendered bundle rejects tag-only images as a production deployment target.

## Environment progression

```text
Development
  local Compose

Staging
  production-like Kubernetes topology
  smaller/non-production data and credentials

Production
  Kubernetes
  HA external stateful dependencies
  approved secret manager
  public TLS ingress
  private backend network
```

Sprint 24 will instantiate the staging environment from this architecture.
