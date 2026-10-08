# Sprint 20 Verification

The generated Sprint 20 package was verified in the packaging environment.

## Shared `smartedu-perf` package

```text
pytest -q
8 passed
```

Coverage includes:

- p95/performance budget evaluation
- error-rate and throughput gates
- percentile interpolation
- connection-pool capacity totals
- Little's Law helper
- estimated RPS helper
- Locust CSV parsing

## Performance configuration tests

```text
pytest -q tests/performance/test_config.py
4 passed
```

Verified:

- the SRS 500-user profile exists and runs for at least 10 minutes
- the soak profile exists and runs for at least 30 minutes
- normal p95 default is 3000 ms
- Attendance p95 budget is 2000 ms
- Notification p95 budget is 5000 ms
- role/action workload weights sum to 100
- the candidate scaling configuration covers all core backend services

## Connection budget

The candidate shared-PostgreSQL model was evaluated:

```text
steady_total=113
burst_total=180
usable_connections=220
PASS
```

The model assumes:

```text
PostgreSQL max_connections = 250
reserved operational connections = 30
```

This is a candidate capacity model only; the real Sprint 17 settings and final
replica counts must be reconciled during integration.

## Wheel build

Built successfully:

```text
smartedu_perf-0.1.0-py3-none-any.whl
```

using:

```text
python -m pip wheel . --no-deps --no-build-isolation
```

The wheel is not stored in the Sprint ZIP; reproducible package source and build
scripts are included.

## Synthetic Locust result evaluation

`evaluate-performance.py` was run against synthetic Locust CSV data.

Results:

```text
PASS attendance.read       p95=1200ms error=0.20% rps=50
PASS notifications.inbox   p95=1400ms error=0.10% rps=40
```

The generated evaluation JSON was then compared against itself with
`compare-performance.py`:

```text
No configured performance regression detected.
```

## Python syntax

All generated Python files compile successfully.

## Configuration parsing

All generated JSON/YAML files parse successfully.

## Encoding

UTF-8 BOM scan:

```text
0 BOM files
```

## Important runtime limitations

The packaging environment does not have these runtime packages installed:

```text
locust
psycopg
redis
aio-pika
```

`boto3` is available.

Therefore the following are not claimed as executed here:

- real Locust smoke/baseline/500-user/stress/soak runs
- distributed Locust master/worker Compose run
- PostgreSQL live diagnostics/query-plan capture
- Redis benchmark
- RabbitMQ benchmark
- MinIO/S3 benchmark against a live QA store
- Attendance mutation load
- Notification end-to-end latency probe
- Playwright browser performance test
- service CPU/memory/DB pool observations
- real candidate replica scaling comparison
- real performance baseline/candidate regression comparison

These are repository/QA-environment integration requirements in
`SPRINT_20_INTEGRATION.md` and `CODEX_MERGE_PROMPT.md`.

## Not a production capacity claim

Sprint 20 provides the tooling, workloads, budgets, runbooks, and candidate
capacity model.

It does **not** claim the Smart Education Platform already sustains 500 users or
meets the 3s/2s/5s targets until those tests are run against the user's merged
staging environment.
