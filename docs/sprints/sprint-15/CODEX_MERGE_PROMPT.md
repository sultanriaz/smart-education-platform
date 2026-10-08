Integrate Sprint 15 Complete Admin UX into the current Smart Education Platform.

FIRST inspect the actual merged Sprints 1–14. The final result must be a real
Admin workflow, not placeholder pages.

Preserve Student and Teacher UX and all service boundaries.

1. Identity
   Reconcile the actual Sprint 1 user/role/permission APIs.
   Verify Admin:
   - lists users
   - creates users
   - changes active/verified state
   - assigns roles
   - creates roles with valid permission codes

   Do not invent password reset/email verification if those endpoints do not
   exist.

2. Academic — highest-priority reconciliation
   Sprint 2 was implemented locally and is not bundled in Sprint 15.

   Read its actual OpenAPI, entities, schemas, and tests.

   Adapt the frontend Academic Admin adapter to the exact domain:
   - departments
   - programs
   - academic years
   - semesters
   - courses / course offerings if used
   - sections
   - Student profiles
   - Teacher profiles
   - enrollments
   - teaching assignments

   Implement missing Admin edit/deactivate/withdraw/unassign UI actions using the
   REAL Sprint 2 endpoints if the current frontend only has create/list coverage.

   Preserve:
   - UUID service boundaries
   - duplicate enrollment prevention
   - section capacity row locking
   - semester/program compatibility
   - Teacher assignment validation
   - no direct Identity DB foreign keys
   - no cross-service DB access

3. Scheduling
   Reconcile against Sprint 4 exact contract.
   Verify create/cancel/override flows and all conflict rules.

4. Facilities
   Reconcile against Sprint 6 exact schemas.
   Verify:
   - facility CRUD
   - bookability
   - Admin sees all bookings
   - approval/rejection
   - facility blocks
   - no double-booking regression

5. Notifications
   Reconcile Sprint 5 Admin template/campaign APIs.
   Preserve Sprint 14 restricted Teacher announcements.
   Test role and section campaigns plus preference handling.

6. Reporting
   Reconcile Sprint 9 overview, six metric endpoints, snapshots, and authenticated
   CSV export.

7. Platform
   Reconcile Sprint 10:
   - service registry
   - health sweep
   - settings
   - feature flags
   - jobs
   - support queue
   - audit log

   Never expose secrets through settings or Vite/runtime config.

8. Frontend Admin RBAC
   Routes:
   - /app/admin
   - /app/admin/users
   - /app/admin/academic
   - /app/admin/scheduling
   - /app/admin/facilities
   - /app/admin/notifications
   - /app/admin/reporting
   - /app/admin/platform

   Student and Teacher tokens must be denied by both frontend guards and backend
   services.

9. Gateway
   Every browser request must go through Sprint 11 Gateway.
   No direct :8001–:8010 URLs.
   Do not expose internal APIs.

10. Run frontend:
    - npm install
    - npm run typecheck
    - npm run lint
    - npm run test
    - npm run build
    - Docker build
    - /health
    - deep-link SPA refresh

11. Run every relevant service regression:
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
    - Gateway

12. Run the complete Admin E2E flow in SPRINT_15_INTEGRATION.md.

13. Security checks:
    - non-Admin backend requests to Admin APIs -> 403
    - no cross-service database reads
    - no secrets returned to frontend
    - Platform settings contain only safe runtime/application configuration
    - Notification Admin campaign rights are not inherited by Teacher
    - Facility approval rights are not inherited by Student/Teacher
    - Student answer keys remain protected
    - Teacher cannot inspect IN_PROGRESS Student attempts

At completion report:
- exact Sprint 2 Academic route/schema adaptations
- any Admin edit/deactivate actions added during merge
- exact Identity contract used
- exact test totals for every service
- frontend typecheck/lint/test/build results
- Docker results
- Gateway/CORS results
- complete Admin E2E results
- remaining assumptions
