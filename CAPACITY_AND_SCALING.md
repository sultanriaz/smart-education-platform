# Capacity and Scaling Architecture

Sprint 23 turns the Sprint 20 measured candidate topology into deployable HPA
configuration.

## Starting replica counts

Critical/high-traffic candidates:

```text
Academic   3
Attendance 3
Assessment 3
```

Other application workloads start at two replicas.

These values are not proof of production capacity.

## HPA

Each workload has an `autoscaling/v2` HPA using candidate CPU and memory targets:

```text
CPU    70%
memory 75%
```

Scale-up is faster than scale-down.

Scale-down uses a five-minute stabilization window to avoid rapid oscillation.

## HPA limitations

CPU/memory alone do not capture all distributed bottlenecks.

The final deployment may add custom scaling signals after staging evidence:

```text
request concurrency
p95 latency
DB pool wait
RabbitMQ queue age
worker queue depth
```

Do not autoscale API replicas aggressively when PostgreSQL is already connection
or lock constrained.

## Resource requests and limits

Every container receives explicit requests and limits.

The generated values are starting budgets and must be measured in staging.

Too-low CPU limits can create throttling; too-high requests can prevent
scheduling.

## Cluster capacity

The production cluster must have headroom for:

```text
current replicas
HPA scale-up
rolling-update surge pods
node maintenance
system/Ingress/observability workloads
```

Do not size the cluster only for the normal steady-state replica total.

## Database connection budget

When HPA maximum replicas change, recalculate the Sprint 20 PostgreSQL connection
budget.

A deployment is incomplete if maximum pod count can theoretically exhaust the
database before HPA reaches its configured maximum.
