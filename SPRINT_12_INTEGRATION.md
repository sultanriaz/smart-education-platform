# Sprint 12 Integration — Frontend Foundation

Expected additions:
- `apps/frontend`
- `docker-compose.frontend.yml`
- `.github/workflows/frontend-ci.yml`

## Mandatory reconciliation

Inspect actual Sprints 1–11.

### Identity
Verify exact login, refresh, logout, registration, `/users/me`, role, and token
rotation contracts. Adapt frontend adapters rather than weakening Identity.

### Gateway
Verify the actual Sprint 11 namespace map. Browser application code should use one
gateway base URL, not individual service host ports.

### CORS
Vite origin: `http://localhost:5173`  
Docker frontend origin: `http://localhost:3000`

If both must be allowed simultaneously, extend Sprint 11 to an explicit
multi-origin allow-list; do not use wildcard CORS with credentials.

## Required smoke flow

1. Start Identity and Gateway.
2. Start frontend.
3. Register a Student if enabled.
4. Login as Student.
5. Reload and verify session restoration.
6. Confirm Student-only navigation.
7. Verify an Admin URL is denied.
8. Logout.
9. Login as Teacher and verify Teacher navigation.
10. Login as Admin and verify Admin navigation.
11. Force an expired access token and verify exactly one refresh/retry.
12. Revoke the refresh token and verify session clearing.
13. Refresh a deep SPA URL and verify Nginx serves the app.
14. Inspect browser traffic and verify API calls use Gateway only.
