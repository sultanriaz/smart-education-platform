# Sprint 20 Database Performance Engineering

## Measure first

Use:

```text
pg_stat_activity
pg_stat_user_tables
pg_stat_user_indexes
pg_stat_statements
EXPLAIN (ANALYZE, BUFFERS)
```

Do not create speculative indexes solely because a column appears in a filter.

## High-priority query families

Review the actual merged queries for:

```text
Identity:
  email/user lookup
  refresh token lookup/revocation
  roles/permissions

Academic:
  semester/course/section lookup
  enrollment
  teacher assignment
  roster

Attendance:
  session by section/date
  student attendance summary
  session records

Scheduling:
  room/Teacher/section interval conflicts
  occurrence lookup

Notification:
  user unread/read/archive
  outbox/inbox
  delivery attempts

Facility:
  availability/overlap
  booking history

Learning:
  course/section targeting
  published resources
  versions

Assessment:
  assignment/student
  attempt number/limit
  grading queues

Reporting:
  projection dimensions
  occurred_at/date filters

Platform:
  audit timestamp/actor/resource filters
  jobs/status
```

## Index rules

Indexes should support proven access paths.

For multi-column indexes, column order must match the actual predicates and
sorting pattern.

Partial indexes can be useful for small active subsets such as:

```text
pending outbox
unread notifications
active bookings
in-progress jobs
```

but only after verifying the real query and write cost.

## Query-plan review

Capture both representative small and realistic-sized datasets.

Look for:

```text
large sequential scans
high rows removed by filter
nested-loop amplification
temp-file spills
sort/hash memory pressure
lock waits
N+1 ORM access
repeated identical queries
```

## Pool sizing

Pool size is a concurrency budget, not a performance knob to maximize.

For one physical PostgreSQL target:

```text
sum(replicas × (pool_size + max_overflow))
```

must leave operational headroom under `max_connections`.

Use:

```powershell
python .\scripts\check-connection-budget.py
```

The included budget is a candidate model, not a production sizing claim.
