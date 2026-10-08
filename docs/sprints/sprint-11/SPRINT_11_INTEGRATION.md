# Sprint 11 Integration — API Gateway / Edge Layer

Sprint 11 introduces a single intended public backend entry point.

## Required repository changes during merge

The gateway package itself does not modify existing Sprint 1-10 Compose files.
The integration pass must inspect each API service and attach only its API
container to the shared external Docker network:

```text
smart-education-edge
```

Expected DNS names or configured upstreams:

- identity-service
- academic-service
- attendance-service
- scheduling-service
- notification-service
- facility-service
- learning-service
- assessment-service
- reporting-service
- platform-service

If an actual Compose service name differs, configure the gateway upstream
environment variable to the real DNS name.

## Public API contract

Use the namespaced external routes:

- `/api/v1/identity/*`
- `/api/v1/academic/*`
- `/api/v1/attendance/*`
- `/api/v1/scheduling/*`
- `/api/v1/notifications/*`
- `/api/v1/facilities/*`
- `/api/v1/learning/*`
- `/api/v1/assessments/*`
- `/api/v1/reporting/*`
- `/api/v1/platform/*`

Each namespace is rewritten to the target service's `/api/v1/*`.

Do not expose service `/internal` APIs through public gateway routes.

## Integration checks

Verify:

1. Identity login through gateway.
2. Refresh through gateway.
3. Authenticated Academic request.
4. Attendance request.
5. Scheduling request.
6. Notification request.
7. Facility request.
8. Learning request.
9. Assessment request.
10. Reporting admin request.
11. Platform search/support request.
12. Authorization headers survive proxying.
13. `X-Request-ID` arrives at services.
14. CORS preflight works from the actual frontend origin.
15. 502/504 becomes normalized 503 JSON.
16. oversized request becomes normalized 413.
17. rate limiting yields normalized 429.
18. direct `/api/v1/internal/...` has no public route.
19. databases are not attached to the edge network.
20. direct host ports for backend services can eventually be removed from
    staging/production after gateway verification.

## Important

For local development it is acceptable to keep individual service host ports
temporarily for debugging. Production should expose only the frontend and the
gateway/load balancer unless another explicit public endpoint is required.
