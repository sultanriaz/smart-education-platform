# Sprint 23 → Sprint 24 Staging Handoff

Sprint 24 should instantiate the same architecture defined here with isolated
non-production identities, data, secrets, and DNS.

Staging should preserve:

```text
Kubernetes scheduling model
Ingress/Gateway routing
TLS
NetworkPolicy
per-service secrets
separate service databases
Redis cache/durable split
RabbitMQ
object storage
observability
release-manifest image pinning
```

Staging may use smaller managed tiers and lower HPA maximums, but it should not
replace distributed service boundaries with a monolith.

Sprint 24 must verify:

```text
clean environment bootstrap
all migrations
all 12 workloads
Gateway/frontend routing
Student/Teacher/Admin E2E
event flows
backup/restore rehearsal
pod/node failure
rolling deployment
Sprint 20 load smoke
Sprint 21 telemetry
Sprint 22 release promotion
```
