Integrate Sprint 13 Student UX into the current Smart Education Platform.

FIRST inspect the actual merged Sprints 1–12. Reconcile real API contracts
instead of changing backend rules merely to match this package.

This sprint must result in a genuinely working Student workflow, not just UI
screens.

1. Frontend foundation
   Preserve Sprint 12:
   - React Router
   - TanStack Query
   - Tailwind
   - shared API client
   - one-time 401 refresh
   - AuthProvider
   - RBAC
   - runtime Gateway config
   - accessible responsive shell

2. Attendance integration
   Reconcile actual Attendance routes and schemas.
   Student must only receive their own records.
   Use backend percentage values/rules; do not invent frontend attendance logic.

3. Scheduling integration
   Reconcile `/timetable/me`.
   Ensure Student receives expanded date/time occurrences suitable for the UI.

4. Learning integration
   Reconcile Student resources and recommendations.
   Verify authenticated download works through Gateway.
   Do not expose object-storage private credentials or bypass authorization.

5. Assessment integration
   The original Sprint 8 package lacked Student read/list endpoints. Sprint 13
   includes `student_read.py` as an additive compatibility patch.

   Inspect the actual Sprint 8 implementation before applying it.

   Required Student capabilities:
   - list visible assigned assessments
   - get one visible assignment with questions
   - NEVER expose correct choices, correct_text, explanations, or grading keys
   - list own results
   - start own attempt
   - save own answers
   - submit own attempt
   - enforce attempt limits/deadlines server-side
   - objective auto-grading stays backend-owned
   - subjective grading stays backend-owned

   If Academic Service can expose a batch/current-enrollment endpoint, prefer it
   over an N+1 validation call for every assignment, while preserving service
   boundaries.

6. Facility integration
   Reconcile Facility list/bookings/create/cancel schemas.
   Backend remains authoritative for availability, double-booking protection,
   notice windows, duration limits, blocks, and cancellation policy.

7. Notification integration
   Reconcile inbox, unread count, mark-read, mark-all, and preferences.
   Student must not access admin campaign/template endpoints.

8. Profile
   Keep Identity-backed profile working.
   If Academic Service exposes an authenticated Student academic profile, add it
   as a read-only section without cross-database access.

9. RBAC/security
   Verify Student cannot open Teacher/Admin routes.
   Verify Student cannot request other users' private resources by changing IDs.
   Verify Assessment assignment responses contain no answer keys.

10. Gateway
    All browser calls must go through Sprint 11 Gateway.
    No direct :8001–:8010 URLs in frontend source.

11. Run frontend:
    - npm install
    - npm run typecheck
    - npm run lint
    - npm run test
    - npm run build
    - Docker frontend build

12. Run relevant backend:
    - Assessment pytest including new Student read-contract test
    - Attendance tests
    - Scheduling tests
    - Learning tests
    - Facility tests
    - Notification tests
    - Identity regression tests
    - Gateway tests

13. Live Student smoke:
    - login
    - dashboard
    - attendance
    - timetable
    - resource download
    - recommendation
    - assessment attempt/submit
    - result display
    - facility booking/cancel
    - notification read/preferences
    - profile
    - RBAC denial
    - deep-link refresh

14. Browser network inspection:
    verify all API traffic uses Gateway only.

At completion report:
- every API contract adaptation
- whether Assessment Student read APIs were added/changed
- confirmation that answer keys cannot leak
- exact frontend tests/typecheck/lint/build results
- exact backend regression results
- Student E2E smoke results
- remaining assumptions
