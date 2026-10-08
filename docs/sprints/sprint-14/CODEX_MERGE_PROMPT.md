Integrate Sprint 14 Complete Teacher UX into the current Smart Education Platform.

FIRST inspect the actual merged Sprints 1–13. Reconcile contracts instead of
weakening service boundaries or authorization.

The final result must be a real Teacher workflow, not placeholder screens.

1. Preserve Sprint 13 Student UX and Sprint 12 frontend foundation.

2. Academic:
   Reconcile current-Teacher assigned-section and section-roster endpoints.
   Teacher must only see authorized academic sections/rosters.
   No cross-service database access.

3. Attendance:
   Reconcile the real Sprint 3 routes with the Teacher adapter.
   Required:
   - section sessions
   - create session
   - attendance sheet
   - bulk save
   - finalize/lock
   - correction with reason
   - authorization against assigned Teacher section
   Preserve transaction behavior and audit history.

4. Scheduling:
   Sprint 4 `/timetable/me` requires start_date/end_date.
   Verify the two-week frontend request and occurrence normalization.

5. Learning:
   Reconcile Sprint 7 resource schemas.
   Test:
   - create NOTE/LINK/VIDEO/FILE
   - add versions
   - file upload
   - publish
   - archive
   - unauthorized target rejection
   Do not bypass Learning ownership/target checks.

6. Assessment:
   Sprint 14 adds Teacher read APIs and hardens authoring/grading.

   Preserve Sprint 13 Student read APIs.

   Verify:
   - Teacher lists own banks/questions/quizzes
   - Teacher sees assessments for sections they are assigned to
   - Teacher cannot mutate another Teacher's content
   - Teacher cannot assign to unassigned section
   - Teacher cannot see IN_PROGRESS Student answers
   - Teacher can see SUBMITTED/GRADED attempts
   - Teacher can manually grade subjective answers only after submission
   - grading reason/audit is retained
   - Student answer keys remain hidden
   - Admin global management still works

   If the merged Academic API offers a batch endpoint for Teacher assignments,
   use it to avoid N+1 validation without creating DB coupling.

7. Notification:
   Sprint 14 adds section-scoped Teacher announcements.

   Verify the Academic assignment-validation route:
   `/api/v1/teachers/{teacher_user_id}/sections/{section_id}/assignment`
   or adapt it to the real Sprint 2 equivalent.

   Teacher announcement endpoint must never permit:
   - ROLE campaigns
   - arbitrary DIRECT campaigns
   - unassigned SECTION campaigns
   - Admin template management

8. Facility:
   Use Sprint 6 exact BookingCreate and BookingCancel schemas.
   Teacher can create/list/cancel own bookings.
   Teacher cannot approve/reject bookings.

9. Frontend RBAC:
   Teacher routes:
   - dashboard
   - attendance/classes
   - timetable
   - learning
   - assessments
   - announcements
   - facilities
   - notifications
   - profile

   Student and Admin-only routes remain denied to a Teacher unless the actual
   product policy intentionally grants a combined role.

10. Gateway:
    All browser API calls use Sprint 11 Gateway.
    No direct :8001–:8010 calls.

11. Run frontend:
    - npm install
    - npm run typecheck
    - npm run lint
    - npm run test
    - npm run build
    - Docker frontend build
    - SPA deep-link refresh

12. Run backend regressions:
    - Identity
    - Academic
    - Attendance
    - Scheduling
    - Notification including Sprint 14 announcement tests
    - Facility
    - Learning
    - Assessment including Sprint 13 + Sprint 14 tests
    - Gateway
    - Student Sprint 13 regressions

13. Run full Teacher browser smoke flow from SPRINT_14_INTEGRATION.md.

14. Inspect browser network traffic:
    every application API call must target Gateway.

15. Do not solve integration problems by:
    - querying another service DB
    - importing another service ORM models
    - removing authorization
    - exposing internal endpoints publicly
    - leaking Assessment answer keys
    - allowing Teacher global Notification campaigns

At completion report:
- every Academic/Attendance route adaptation
- exact Assessment hardening changes
- exact Notification Teacher-announcement changes
- exact test totals
- typecheck/lint/build results
- Docker results
- complete Teacher E2E smoke results
- remaining assumptions
