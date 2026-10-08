Integrate Sprint 16 Distributed Contract & Resilience Hardening into the current
Smart Education Platform.

FIRST inspect the actual merged Sprints 1–15. Do not blindly overwrite service
entrypoints or domain-specific error handling.

The result must harden the distributed architecture without converting it into a
monolith or creating cross-service database access.

1. Shared Python package

   Integrate:
   `libs/python/smartedu_contracts`

   Build/install it in every Python service environment and Docker image.

   Keep one shared package; do not copy/paste the implementation into services.

2. Wire all ten FastAPI services

   Each service has additive:
   `services/<service>/app/sprint16.py`

   Wire `install_sprint16(app)` into:
   - Identity
   - Academic
   - Attendance
   - Scheduling
   - Notification
   - Facility
   - Learning
   - Assessment
   - Reporting
   - Platform

   The included `scripts/apply_sprint16_wiring.py` may perform the mechanical
   import/call insertion. Inspect its diff afterward.

   Preserve existing domain exception semantics. Migrate response shape without
   losing domain status/code information.

3. Request and workflow context

   Verify every service:
   - accepts/propgates X-Request-ID
   - accepts/propagates X-Correlation-ID
   - accepts X-Causation-ID
   - returns X-Request-ID
   - returns X-Correlation-ID
   - logs enough context for later observability work

   Gateway remains authoritative for the public request ID.

4. Gateway

   Merge Sprint 16:
   - `infra/gateway/nginx.conf`
   - `infra/gateway/snippets/proxy_common.conf`
   - `infra/gateway/templates/default.conf.template`
   - Sprint 16 Gateway tests

   Verify:
   - internal routes remain blocked
   - CORS allows correlation/idempotency headers
   - X-Correlation-ID is sanitized
   - invalid correlation IDs fall back to Gateway request ID
   - gateway errors contain request_id and correlation_id
   - raw Idempotency-Key values are not logged
   - existing routing/rate-limit/security tests remain green

5. Frontend

   Merge Sprint 16 `apps/frontend/src/lib/api-client.ts`.

   Preserve all Sprint 13–15 APIs.

   Verify:
   - GET has no Idempotency-Key
   - POST/PUT/PATCH/DELETE receive one
   - 401 token refresh retry uses the SAME key
   - API errors expose requestId/correlationId
   - file download remains authenticated
   - Student/Teacher/Admin flows regress cleanly

6. Idempotency

   Development can use MemoryIdempotencyStore.

   Staging/production must use Redis:
   `IDEMPOTENCY_REDIS_URL`

   Add Redis dependency/config where needed without sharing service databases.

   Test:
   - same key + same mutation => replay original response
   - replay has X-Idempotent-Replay: true
   - same key + different request => 409 idempotency_conflict
   - concurrent same key while first is processing => 409 idempotency_in_progress
   - 5xx is not permanently cached
   - multi-replica retry is protected by Redis store

7. Service-to-service resilient HTTP

   Inspect ALL raw httpx usage and migrate dependency clients where appropriate
   to `ResilientHttpClient`.

   Priority graph:
   Attendance   -> Academic
   Scheduling   -> Academic
   Notification -> Identity
   Notification -> Academic
   Learning     -> Academic
   Assessment   -> Academic
   Facility     -> Notification
   Platform     -> service health endpoints

   Every synchronous dependency call must have:
   - finite timeout
   - request/correlation propagation
   - bounded retry
   - circuit breaker
   - no retry of POST/PATCH without Idempotency-Key

   Do not blindly retry domain 4xx responses.

8. Internal service authentication

   Migrate static INTERNAL_SERVICE_TOKEN / INTERNAL_EVENT_TOKEN usage to
   short-lived EdDSA service tokens.

   Use:
   - one Ed25519 private key per service
   - public keys only in target trust stores
   - audience = target service
   - least-privilege scopes from
     `contracts/security/service-scopes.yaml`

   Do not reuse Identity user-JWT private keys.

   Use a staged migration:
   - target accepts signed token + temporary legacy token
   - callers migrate
   - staging verifies
   - legacy path disabled
   - old static secret removed

   Report any service that still requires legacy-token compatibility.

9. Events

   Adopt `EventEnvelope` v1 for new/updated cross-service events.

   Inspect existing:
   - Facility outbox -> Notification
   - Notification inbox/outbox
   - Reporting event ingestion
   - Platform audit/event ingestion
   - any Scheduling/Attendance/Learning/Assessment event emitters

   Add compatibility adapters where necessary instead of deleting established
   inbox/outbox reliability code.

   Verify:
   - event_id deduplication
   - event_version
   - timezone-aware UTC occurred_at
   - correlation_id
   - causation_id where known
   - producer owns transaction/outbox
   - consumers are safe under at-least-once delivery

10. Ownership boundaries

   Use `contracts/service-ownership.yaml`.

   Search the repository for:
   - cross-service ORM imports
   - direct another-service DB URLs
   - direct another-service SQL
   - browser service-port calls

   Fix any violations through HTTP/events/contracts, not shared domain models.

11. API versioning and pagination

   Keep existing `/api/v1`.

   Do not make breaking response changes just for Sprint 16.

   Use canonical Page/error contracts for new endpoints and migrate legacy
   endpoints with compatibility tests.

12. Docker

   Integrate the shared package into all service images using
   `infra/docker/SPRINT_16_DOCKER_PATTERN.md`.

   Private service signing keys must enter containers only via deployment secret
   mechanisms.

13. Tests

   Run shared package:
   `cd libs/python/smartedu_contracts && pytest -q`

   Run Gateway full suite.

   Run frontend:
   - npm install
   - npm run typecheck
   - npm run lint
   - npm run test
   - npm run build

   Run every service's complete pytest suite.

14. Failure/resilience integration tests

   Add and run tests for:
   - dependency timeout
   - 503 retry
   - circuit opening
   - circuit recovery
   - no unsafe POST retry
   - safe idempotent mutation retry
   - wrong internal JWT audience
   - expired service JWT
   - missing service scope
   - untrusted service signer
   - duplicate event
   - idempotency replay/conflict/in-progress
   - malformed correlation ID
   - Gateway downstream 503 envelope

15. End-to-end regression

   Run complete:
   - Student flow
   - Teacher flow
   - Admin flow

   Confirm browser network calls still go only through Gateway.

16. Do not solve Sprint 16 by:
   - sharing service ORM models
   - querying another service database
   - globally retrying all POSTs
   - storing private keys in Git
   - exposing internal endpoints at Gateway
   - using Platform settings as a secret store
   - disabling authorization to make contract tests pass

At completion report:
- all main.py wiring changes
- every raw httpx client migrated
- static-token migration status per caller/target
- exact internal service scopes used
- event producers/consumers migrated or compatibility-wrapped
- idempotency backend per environment
- Gateway test results
- shared package test results
- frontend results
- service test totals
- Student/Teacher/Admin E2E results
- remaining legacy compatibility items
