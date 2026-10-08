# PostgreSQL Concurrency Test Plan

Concurrency correctness must be verified against PostgreSQL, not SQLite.

## Pattern

Each contender uses:

- a separate SQLAlchemy Session/connection
- a barrier so both operations begin together
- the real production transaction boundary
- unique test data
- bounded worker timeout

Assert both:

```text
exactly one winning business operation
database constraints/invariants remain valid
```

## Academic

Final seat:

```text
section capacity = 1
two eligible Students enroll concurrently
expected: one success, one conflict
```

Duplicate enrollment:

```text
same Student/course/section race
expected: one persisted enrollment
```

## Attendance

Same Student/session record:

```text
two bulk writes concurrently
expected: no duplicate record
```

Finalize vs mutation:

```text
finalize session races with edit
expected: no post-finalization write committed
```

## Scheduling

Two schedules compete for:

```text
same room/time
same Teacher/time
same section/time
```

Expected: one winner.

Adjacent intervals must both succeed.

## Facility

Two users book the same facility/time.

Expected: one booking reaches the accepted/held state.

## Assessment

Attempt limit = 1.

Two start-attempt requests race.

Expected: exactly one attempt.

## Idempotency

Two replicas receive same:

```text
Idempotency-Key
method
path
body
```

Expected:

```text
one execution
one replay/in-progress response
no duplicate side effect
```

## Outbox

Two publisher workers claim pending events.

Expected:

```text
one broker publish per claim cycle
no event permanently lost
duplicate publish remains consumer-safe through event_id inbox deduplication
```
