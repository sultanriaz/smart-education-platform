# HTTP Contract v1

All public APIs remain under `/api/v1`.

## Request context headers

- `X-Request-ID`
  - created by the Gateway for public traffic
  - propagated unchanged by downstream services
  - identifies one HTTP request

- `X-Correlation-ID`
  - identifies one logical workflow across service calls/events
  - Gateway accepts only a restricted safe value and otherwise generates one
  - internal HTTP clients propagate it

- `X-Causation-ID`
  - optional
  - identifies the request/event directly responsible for a new call/event

- `Idempotency-Key`
  - optional for mutating browser requests
  - mandatory for mutating service-to-service requests that can be retried
  - same key + same method/path/query/body may replay
  - same key + different request returns `409 idempotency_conflict`

## Error envelope

Canonical service/gateway-generated errors:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "request_id": "request-id",
    "correlation_id": "workflow-id",
    "details": {}
  }
}
```

Existing service-specific errors can migrate incrementally. Do not change domain
semantics merely to change the error shape.

## Pagination

New list endpoints should return:

```json
{
  "items": [],
  "page": {
    "offset": 0,
    "limit": 50,
    "count": 0,
    "total": 0
  }
}
```

Existing endpoints are not broken in Sprint 16. Add compatibility adapters where
the frontend currently consumes legacy list shapes.

## Retry contract

A client may automatically retry:

- GET
- HEAD
- OPTIONS
- PUT
- DELETE

on transport errors or `429/502/503/504`, within a bounded retry budget.

POST/PATCH may be retried only when the operation is protected by a stable
`Idempotency-Key`.

Domain `4xx` failures are not retryable.

## Timeouts

Every service-to-service HTTP call must set a finite connect/read timeout.

A service must fail fast rather than waiting indefinitely for another service.

## API versioning

Breaking public HTTP changes require a new public API version such as `/api/v2`.

Backward-compatible additions stay in `/api/v1`.

Event compatibility is versioned independently through `event_version`.
