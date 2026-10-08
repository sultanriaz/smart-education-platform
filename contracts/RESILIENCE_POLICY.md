# Cross-Service Resilience Policy

## Timeout

Every outbound HTTP dependency call uses a finite timeout.

Default baseline:

```text
connect/read timeout: 3 seconds
```

Long-running export/upload workflows should use asynchronous jobs rather than
raising general dependency timeouts globally.

## Retry

Automatic retry is bounded to three attempts by default.

Retryable failures:

```text
transport failure
429
502
503
504
```

Safe methods:

```text
GET
HEAD
OPTIONS
PUT
DELETE
```

`POST` and `PATCH` are retryable only when the caller supplies a stable
`Idempotency-Key`.

Do not retry domain validation/authentication/authorization failures.

## Circuit breaker

Default process-local baseline:

```text
failure threshold: 5
recovery window: 15 seconds
```

The circuit breaker exists to prevent one degraded dependency from consuming all
request capacity.

It is intentionally process-local. A distributed circuit state is not required
for correctness.

## Idempotency

Browser mutation requests receive a generated Idempotency-Key from the Sprint 16
API client.

Service-to-service mutations that can retry must explicitly supply their own
stable key based on the logical operation/event.

Development can use `MemoryIdempotencyStore`.

Production must use the Redis-backed store when multiple replicas can serve the
same endpoint.

## Event delivery

At-least-once delivery is expected.

Consumers must deduplicate by `event_id`.

A successfully processed duplicate event returns success rather than executing
the side effect twice.

## Failure boundaries

A service may return `503` when a required synchronous dependency is unavailable.

Do not silently read another service's database as a fallback.

Where the workflow tolerates eventual consistency, prefer outbox/event
publication over synchronous coupling.
