# Sprint 24 Staging Architecture

Sprint 24 instantiates the Sprint 23 deployment architecture as an isolated,
production-like staging environment.

## Goal

Staging is the environment where a Sprint 22 immutable release is proven before
production-readiness work.

It must be similar enough to production to expose:

```text
service discovery problems
migration problems
secret/config problems
Ingress/TLS problems
NetworkPolicy problems
event/broker problems
object-storage permissions
distributed tracing/metrics issues
rolling-deployment issues
multi-replica concurrency issues
backup/restore weaknesses
```

## Staging topology

```text
Internet / approved test network
        |
      HTTPS
        |
Staging load balancer / Ingress
        |
   +----+-----+
   |          |
Frontend   API Gateway
              |
  +-----------+----------------------------------+
  |      |       |       |       |       |      |
Identity Academic Attendance Scheduling Notification ...
              |
       private staging dependencies
              |
 PostgreSQL / Redis / RabbitMQ / Object Storage
```

Namespace:

```text
smartedu-staging
```

The generated source hostname:

```text
staging.smartedu.example.edu
```

is a placeholder. Strict preflight rejects placeholder domains.

## Application replicas

All 12 application workloads use at least two replicas in staging.

This is intentional even though staging is smaller than production.

It allows validation of:

```text
load balancing
rolling update
pod failure
distributed idempotency
shared Redis state
database locking
multi-replica behavior
```

A one-replica staging environment cannot validate these properties.

## Stateful dependencies

The application manifests do not install PostgreSQL/Redis/RabbitMQ/object
storage inside application pods.

Staging dependencies can be:

```text
managed non-production tiers
dedicated staging clusters
approved in-cluster stateful services
```

provided they preserve the real product semantics required by Sprints 17–23.

The exact provider is environment-specific.

## Isolation

Staging must use separate:

```text
DNS hostname
TLS certificate
Kubernetes namespace/cluster credentials
PostgreSQL databases/accounts
Redis databases/clusters
RabbitMQ vhost/users
object-storage buckets
email sandbox account
Identity signing/security secrets
QA user accounts
observability environment labels
```

Do not point staging services at production data stores.

## Release source

Staging deploys only Sprint 22 release manifests.

The flow is:

```text
Git release tag
  ↓
release-manifest.json
  ↓
Sprint 24 renderer
  ↓
digest-pinned staging Kubernetes bundle
  ↓
migration jobs
  ↓
application rollout
  ↓
acceptance gates
```

Staging is not a place to build different images from the production candidate.
