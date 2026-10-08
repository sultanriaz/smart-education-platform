# Sprint 20 Cache Strategy

Caching exists to reduce repeat read cost, not to repair slow business logic or
hide missing database indexes.

## Cache only derived/repeatable data

Good candidates:

```text
Academic master-data lookup
course/section metadata
JWKS/public-key material
read-only dashboard fragments
resource/category lists
short-lived availability summaries
```

Poor candidates:

```text
password/authentication decisions
permission decisions with long TTL
booking conflict truth
assessment attempt-limit truth
attendance write truth
unpublished answer keys
mutable transaction state
```

Correctness-sensitive source-of-truth state remains in PostgreSQL.

## Redis

Use Sprint 17 `redis-cache` for disposable cache entries.

Every key needs:

```text
namespace
bounded TTL
maximum payload size
invalidation/refresh rule
ownership
```

Example namespace pattern:

```text
smartedu:<env>:<service>:<resource>:<id>:v<schema-version>
```

## Stampede prevention

For expensive cache misses, prefer:

```text
short distributed lock
single refresh
stale-but-safe value where business semantics allow it
```

Do not create one unbounded lock per arbitrary attacker-controlled key.

## TTL guidance

Starting points only:

```text
JWKS/public keys                5-15 minutes + stale fallback
Academic master data           1-5 minutes
Dashboard aggregates           15-60 seconds
Availability summaries         <=15 seconds
Permission/user deactivation   avoid cache or keep very short
```

Measure before and after.

## Performance evidence

For any new cache, capture:

```text
uncached p50/p95/p99
cached p50/p95/p99
DB query reduction
Redis ops/sec
cache hit ratio
memory usage
staleness risk
```

A cache change is incomplete without invalidation tests.
