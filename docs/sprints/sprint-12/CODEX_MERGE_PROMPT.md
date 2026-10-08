Integrate Sprint 12 React + TypeScript + Tailwind Frontend Foundation into the
current Smart Education Platform repository.

FIRST inspect actual Sprints 1–11.

1. Reconcile Identity:
   - login request/response
   - refresh request/response
   - logout
   - registration
   - `/users/me`
   - roles
   - refresh rotation
   - cookie/CSRF behavior if Identity was hardened

2. Reconcile Sprint 11 Gateway namespaces and base URL.
   No frontend feature should call :8001 through :8010 directly.

3. Verify CORS for Vite `http://localhost:5173` and Docker frontend
   `http://localhost:3000`. Use an explicit allow-list, never wildcard
   credentialed CORS.

4. Verify auth/session:
   - login
   - registration
   - reload restoration
   - one refresh on 401
   - no infinite retry
   - refresh rotation
   - logout/revocation
   - failed refresh clears session

5. Verify RBAC:
   Student cannot access Teacher/Admin routes.
   Teacher cannot access Student/Admin routes unless actual product rules permit.
   Admin behavior must match backend policy.

6. Evaluate token storage.
   The package uses sessionStorage for compatibility with the existing JSON-token
   API. If Identity now supports HttpOnly refresh cookies, migrate safely.
   Do not invent a cookie flow if backend support does not exist.

7. Preserve:
   - React Router
   - TanStack Query
   - React Hook Form
   - Zod
   - Tailwind
   - error boundary
   - toasts
   - responsive shell
   - accessible forms/navigation
   - runtime config
   - gateway API client

8. Do not prematurely implement Sprint 13–15 domain pages.

9. Run:
   - npm install
   - npm run typecheck
   - npm run lint
   - npm run test
   - npm run build
   - Docker frontend build
   - frontend `/health`
   - SPA deep-link refresh
   - gateway CORS
   - real Student/Teacher/Admin login
   - access-token refresh
   - logout/revocation
   - protected routes
   - regression tests for Sprints 1–11

10. Inspect browser network traffic. All application APIs must use Gateway.

At completion report exact contract adaptations, tests, build results, auth/RBAC
smoke results, CORS result, and unresolved assumptions.
