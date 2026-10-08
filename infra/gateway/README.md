# Sprint 11 — API Gateway / Edge Layer

Nginx-based edge gateway for the Smart Education Platform.

The gateway is the **only intended public backend entry point** after Sprint 11.

## Why Nginx

The backend services already own authentication/authorization and domain logic.
The gateway's responsibility is edge behavior:

- public routing
- request correlation IDs
- CORS
- rate limiting
- connection limits
- request-size limits
- security headers
- TLS readiness
- upstream timeouts
- gzip
- stable external API namespaces
- normalized gateway-level errors
- hiding internal service ports/topology from clients

It does not own business data and has no database.

## Public namespace

To avoid route collisions between independently designed services, external URLs
are namespaced:

```text
/api/v1/identity/*       -> Identity /api/v1/*
/api/v1/academic/*       -> Academic /api/v1/*
/api/v1/attendance/*     -> Attendance /api/v1/*
/api/v1/scheduling/*     -> Scheduling /api/v1/*
/api/v1/notifications/*  -> Notification /api/v1/*
/api/v1/facilities/*     -> Facility /api/v1/*
/api/v1/learning/*       -> Learning /api/v1/*
/api/v1/assessments/*    -> Assessment /api/v1/*
/api/v1/reporting/*      -> Reporting /api/v1/*
/api/v1/platform/*       -> Platform /api/v1/*
```

Example:

```text
External:
POST /api/v1/identity/auth/login

Internal forwarded request:
POST /api/v1/auth/login
```

This avoids ambiguous routes such as `/api/v1/sections/...`, which are used by
multiple domain services.

## Internal endpoints

The gateway intentionally does not create a generic public route for
`/api/v1/internal/*`, and it explicitly blocks namespaced paths such as
`/api/v1/notifications/internal/*` before they can be rewritten upstream.

Internal service-to-service APIs should remain reachable only on trusted Docker
networks and must retain their internal-token authentication.

## Request IDs

Every request receives a gateway-generated Nginx `$request_id`.

The gateway forwards:

```text
X-Request-ID: <generated-id>
```

to downstream APIs and returns request IDs on gateway-generated error responses.

Source services should eventually log and propagate this same header.

## Error normalization

Gateway-generated failures have a stable JSON shape.

Upstream unavailable:

```json
{
  "error": {
    "code": "upstream_unavailable",
    "message": "A required service is temporarily unavailable",
    "request_id": "..."
  }
}
```

Rate limited:

```json
{
  "error": {
    "code": "rate_limited",
    "message": "Too many requests",
    "request_id": "..."
  }
}
```

Payload too large:

```json
{
  "error": {
    "code": "payload_too_large",
    "message": "Request body is too large",
    "request_id": "..."
  }
}
```

Domain-service error bodies are not rewritten by Nginx.

## Rate limiting

Two zones exist:

- `auth_api`: stricter Identity route limit
- `general_api`: normal API traffic

Defaults:

```text
AUTH_RATE_LIMIT=5r/s
AUTH_RATE_BURST=10

GENERAL_RATE_LIMIT=30r/s
GENERAL_RATE_BURST=60
```

These defaults are development/staging baselines, not final production tuning.

## CORS

Default local frontend:

```text
http://localhost:5173
```

Configure:

```text
CORS_ALLOWED_ORIGIN
```

The gateway uses an exact-origin map rather than reflecting arbitrary origins.

If the frontend later requires multiple production origins, replace the single
environment value with an explicit Nginx allow-list map. Do not use `*` with
credentialed requests.

## Security headers

The gateway sends:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- restrictive `Permissions-Policy`
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Resource-Policy`

CSP should primarily be defined for the frontend application in Sprint 12 because
the gateway currently serves APIs, not the SPA.

## TLS

The local default runs plain HTTP on port `8080`.

A TLS-ready template and Compose override are supplied. Production can either:

1. terminate TLS directly at Nginx, or
2. terminate TLS at a cloud load balancer/Ingress and use trusted internal HTTP
   to the gateway.

Never ship development self-signed certificates as production secrets.

## Shared Docker edge network

Create once:

```powershell
.\infra\gateway\scripts\create-edge-network.ps1
```

Each API service must join:

```text
smart-education-edge
```

Databases, Redis, workers and storage systems should not join the public edge
network merely for convenience.

See `SERVICE_NETWORK_SNIPPET.md`.

## Start gateway

From repository root:

```powershell
.\infra\gateway\scripts\create-edge-network.ps1

docker compose -f .\docker-compose.gateway.yml up -d --build
```

Then:

```text
http://localhost:8080/
http://localhost:8080/health
http://localhost:8080/ready
```

## Static tests

```powershell
cd infra\gateway
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q
```

## Docker integration smoke

From repository root:

```powershell
.\infra\gateway\scripts\integration-smoke.ps1
```

A single mock upstream is given ten Docker DNS aliases so every gateway route can
be tested without starting the whole platform.

## Production hardening still expected later

Sprint 11 lays the edge foundation. Production deployment work later should
include:

- trusted TLS certificates
- production CORS allow-list
- production rate-limit values
- WAF/cloud edge controls if available
- IP forwarding trust configuration behind a load balancer
- centralized gateway logs
- metrics/alerts
- secret management
- Kubernetes/Ingress adaptation if deployed to Kubernetes
