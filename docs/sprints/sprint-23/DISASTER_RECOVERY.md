# Disaster Recovery Strategy

## Failure classes

The architecture distinguishes:

```text
single application pod
single worker node
stateful dependency node
availability-zone failure
bad application release
bad schema/data change
object deletion/corruption
credential compromise
regional/site disaster
```

Each failure requires a different recovery action.

## Application pod/node

Kubernetes reschedules pods and Services remove unhealthy replicas.

PodDisruptionBudgets and at least two replicas reduce planned-maintenance risk.

## Bad release

Sprint 22 rollback can deploy a previous digest-pinned application release only
when the current schema remains backward compatible.

If the schema is not backward compatible, prefer a forward fix.

## Bad migration/data change

Use:

```text
PITR
approved repair migration
forward-fix
```

based on the incident.

Do not automatically execute database downgrades during application rollback.

## Stateful service failure

Use the managed/dedicated HA failover mechanism.

Application readiness should fail closed where a critical dependency is
unavailable.

## Site/region disaster

The exact secondary-region strategy depends on the selected hosting provider and
budget.

Before production launch, define:

```text
secondary region/site
DNS/load-balancer failover
database replication/backup restore path
object-storage replication/restore path
secret recovery
infrastructure recreation procedure
```

Sprint 23 defines the requirement; Sprint 26 production readiness must close
the provider-specific details.

## Recovery validation

Recovery documentation is evidence only after staged drills prove:

```text
who initiates recovery
what data is restored
how integrity is verified
how traffic is re-enabled
how rollback/recovery is audited
```
