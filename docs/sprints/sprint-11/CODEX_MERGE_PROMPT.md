Integrate Sprint 11 API Gateway / Edge Layer into the current Smart Education
Platform repository.

FIRST inspect the actual Sprint 1-10 Docker Compose files, API ports, service
names and route structures. Do not assume the package's upstream names are exact.

Goals:
- one intended public backend entry point
- preserve all existing service boundaries
- do not move business logic into the gateway
- do not make databases public
- do not expose `/internal` service APIs publicly

Required work:

1. Create/confirm shared external Docker network:
   `smart-education-edge`.

2. Attach ONLY API containers that need gateway routing to this network.
   Do not attach PostgreSQL, Redis, Celery workers, MinIO, migration containers,
   etc. unless independently justified.

3. Reconcile actual service DNS names and internal ports with:
   - IDENTITY_UPSTREAM
   - ACADEMIC_UPSTREAM
   - ATTENDANCE_UPSTREAM
   - SCHEDULING_UPSTREAM
   - NOTIFICATION_UPSTREAM
   - FACILITY_UPSTREAM
   - LEARNING_UPSTREAM
   - ASSESSMENT_UPSTREAM
   - REPORTING_UPSTREAM
   - PLATFORM_UPSTREAM

4. Verify actual API paths. External contract should remain namespaced to avoid
   route collisions:
   - /api/v1/identity/*
   - /api/v1/academic/*
   - /api/v1/attendance/*
   - /api/v1/scheduling/*
   - /api/v1/notifications/*
   - /api/v1/facilities/*
   - /api/v1/learning/*
   - /api/v1/assessments/*
   - /api/v1/reporting/*
   - /api/v1/platform/*

5. Make sure Authorization is forwarded unchanged and every upstream receives a
   gateway-generated X-Request-ID.

6. Preserve service-level JWT/RBAC enforcement. Do not make the gateway the sole
   authorization enforcement point.

7. Keep service internal endpoints private. Verify there is no public generic
   proxy to `/api/v1/internal/*`.

8. Reconcile CORS with the actual frontend dev origin. Keep exact allow-list
   behavior. Do not use wildcard origins with credentials.

9. Validate:
   - auth/general rate limits
   - connection limits
   - body-size limit
   - proxy timeouts
   - security headers
   - structured gateway logging
   - gzip
   - WebSocket upgrade forwarding
   - normalized 413/429/503 gateway errors

10. Decide whether TLS terminates:
    - directly at gateway Nginx, or
    - at deployment load balancer/Ingress.
    Keep the supplied TLS template/override valid, but do not generate or commit
    fake production certificates.

11. After gateway routing works, update documentation and frontend-facing API
    base URL conventions so future Sprint 12 frontend calls the gateway, not
    individual service ports.

12. Run:
    - infra/gateway pytest
    - docker build
    - nginx -t with rendered environment
    - mock gateway integration test
    - gateway /health and /ready
    - real Identity login/refresh through gateway
    - one real authorized endpoint per Sprint 1-10 service
    - CORS preflight from frontend origin
    - normalized upstream-down error test
    - rate-limit test
    - request-size test
    - internal-route exposure test
    - regression tests for Sprints 1-10

13. Inspect Docker networking after integration:
    - gateway should resolve service API containers
    - database containers must not be exposed on smart-education-edge solely for
      gateway access

14. Do not remove local debug host ports until integration tests pass. After
    verification, document which ports may be removed in staging/production.

At completion report:
- actual upstream DNS/port mappings
- Compose/network changes
- public route map
- exact test results
- nginx config validation result
- real service smoke results
- CORS/rate-limit/error normalization results
- any route conflicts or unresolved assumptions
