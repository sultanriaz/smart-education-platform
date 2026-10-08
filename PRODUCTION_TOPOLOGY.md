# Production Topology

Canonical candidate topology:

```text
api-gateway           2 replicas
frontend              2

identity-service      2
academic-service      3
attendance-service    3
scheduling-service    2
notification-service  2
facility-service      2
learning-service      2
assessment-service    3
reporting-service     2
platform-service      2
```

HorizontalPodAutoscalers can scale the individual workloads above their minimum
replicas.

The heavier initial replica counts for Academic, Attendance, and Assessment
match the Sprint 20 candidate topology. They must be confirmed by staging load
tests.

## Availability placement

Pods use topology spreading and preferred anti-affinity by hostname.

A production cluster should have enough worker nodes so two replicas of a
critical workload are not forced onto one node.

For multi-zone clusters, Codex/deployment engineering should add a zone-level
spread constraint after confirming the provider's zone labels and topology.

## Application namespace

```text
smartedu
```

Observability may remain in:

```text
smartedu-observability
```

The ingress controller should remain in its own platform namespace.

## Entry points

The only application services routed by public Ingress are:

```text
frontend
api-gateway
```

Domain services must not receive `LoadBalancer` or public `NodePort` Services.

## Runtime configuration

Non-secret runtime values are stored in `smartedu-runtime-config`.

Secrets are created separately from an approved secret store and use one Secret
object per workload.

Do not store production secrets in Kustomize files, GitHub workflow YAML, Git,
or image layers.
