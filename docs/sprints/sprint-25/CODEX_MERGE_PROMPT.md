Integrate Sprint 25 User Acceptance Testing into the actual merged Smart
Education Platform from Sprints 1–24.

FIRST inspect the final SRS, the merged application, Sprint 19 E2E suite,
Sprint 24 staging evidence, and the exact Sprint 22 release candidate.

The goal is formal stakeholder acceptance of the exact immutable release, not
another engineering smoke test.

1. Preserve immutable release identity

   Identify the Sprint 22 `release-manifest.json` accepted in Sprint 24.

   UAT must use exactly:
   - release tag
   - commit SHA
   - all 12 image digests

   Run `scripts/uat-preflight.py`.

   Do not rebuild application images for UAT.

2. Reconcile final SRS

   Read the real final SRS.

   Inspect:
   `config/uat/requirements.yaml`

   Generated requirement IDs are normalized aliases, not claimed formal SRS
   IDs.

   Map them to actual SRS requirement IDs where the source supports them.

   If a project acceptance requirement is not in the SRS, label it as project
   acceptance scope instead of silently attributing it to the SRS.

3. Preserve known SRS NFR meaning

   Reconcile exact IDs/wording for known targets:
   - responsive desktop/mobile
   - 95% normal interactions <=3 seconds
   - >=500 concurrent users
   - Attendance <=2 seconds
   - Notification <=5 seconds
   - 10-minute inactivity logout
   - availability >=99%
   - no normal-operation data loss / recovery target

   Do not weaken those targets in UAT documentation.

4. Review the 40 UAT scenarios

   Catalog:
   `config/uat/scenarios/`

   Confirm every scenario is executable against the actual product.

   Keep coverage across:
   - Student
   - Teacher
   - Admin
   - CrossRole

5. Student UAT

   Reconcile actual UI/routes and ensure scenarios cover:
   - login/workspace
   - timetable
   - attendance
   - learning/private download
   - assessment attempt
   - result privacy/answer-key safety
   - facility booking
   - notifications
   - responsive behavior
   - logout/session protection

6. Teacher UAT

   Reconcile:
   - assigned classes/sections
   - roster
   - attendance session/finalize
   - attendance correction/audit
   - learning publication
   - quiz authoring/assignment
   - grading
   - timetable
   - notifications
   - Admin denial

7. Admin UAT

   Reconcile:
   - academic master data
   - user/role administration
   - scheduling conflict
   - facility decision
   - reporting dashboard
   - report export
   - Platform setting/feature flag
   - support/audit
   - internal Gateway-route blocking

8. Cross-role acceptance

   Preserve:
   - RBAC isolation
   - cross-user privacy
   - inactivity/session behavior
   - performance evidence review
   - availability/failure evidence
   - recovery evidence
   - keyboard usability
   - labels/errors/accessible names
   - responsive core workflows
   - safe/actionable user errors

9. Automated evidence mapping

   Inspect Sprint 19 tests and add `automated_reference` metadata where a UAT
   scenario is supported by a real automated test.

   Do not fabricate test references.

   A manual usability scenario should remain manual/hybrid even if API tests
   exist.

10. Sprint 24 staging evidence

    Link UAT evidence to the actual accepted staging artifacts:
    - deployment state
    - migrations
    - Student E2E
    - Teacher E2E
    - Admin E2E
    - security
    - performance
    - observability
    - recovery/failure drills

    Do not copy a PASS from a different release candidate.

11. UAT environment

    Use accepted staging or a dedicated UAT environment with the same images.

    Verify:
    - HTTPS
    - no placeholder domain
    - non-production data
    - QA/UAT accounts
    - real authorization
    - all distributed service boundaries

12. Participants

    Assign actual:
    - StudentRepresentative
    - TeacherRepresentative
    - AdminRepresentative
    - ProductOwner
    - ProjectSupervisor

    Do not hardcode private participant data into reusable source files.

13. Tester terminology

    Review scenario wording with the final UI.

    Use terminology users actually see:
    - sections/classes
    - attendance
    - timetable
    - learning resources
    - assessments
    - facilities
    - reporting

    Do not expose implementation jargon unnecessarily in human instructions.

14. Accessibility

    Read `UAT_ACCESSIBILITY_USABILITY.md`.

    Determine whether the final SRS/institution mandates a formal standard.

    If WCAG or another standard is actually specified, document the exact
    required level/version and map checks.

    Otherwise keep the practical baseline without claiming unsupported SRS
    language.

15. Responsive UAT

    Use real supported browser/device sizes.

    Confirm critical role tasks remain usable.

16. Defect policy

    Read:
    - `UAT_DEFECT_POLICY.md`
    - `config/uat/defect-policy.yaml`

    Preserve default gate:
    - 0 BLOCKER
    - 0 CRITICAL
    - 0 MAJOR

    Do not downgrade severity simply to pass UAT.

17. Run records

    Use:
    - initialize-uat-run.py
    - record-uat-result.py
    - record-uat-defect.py
    - record-uat-signoff.py
    - complete-uat-run.py

    Keep run JSON machine-readable and release-specific.

18. Evidence

    Follow `UAT_EVIDENCE_POLICY.md`.

    Ensure evidence does not contain:
    - passwords
    - JWTs
    - refresh cookies
    - private keys
    - database/broker credentials
    - real personal data
    - kubeconfig

19. Defect retest

    If a defect fix changes any application image digest, create a new release
    candidate identity.

    Rerun:
    - affected scenarios
    - relevant regression
    - required release prechecks

    Do not reuse old PASS evidence as if it were new execution evidence.

20. Sign-off

    Record human sign-off only after the participant has reviewed results.

    CI must not generate approvals.

    Required:
    - StudentRepresentative
    - TeacherRepresentative
    - AdminRepresentative
    - ProductOwner
    - ProjectSupervisor

21. Gate

    Preserve `config/uat/policy.yaml` unless a documented governance decision
    changes it.

    Default:
    - all P0 PASS
    - all P1 PASS
    - >=95% overall pass rate
    - 0 open BLOCKER
    - 0 open CRITICAL
    - 0 open MAJOR
    - all five signoffs
    - no REJECT signoff

22. Traceability

    Run `validate-uat-catalog.py`.

    Generate `UAT_REQUIREMENTS_TRACEABILITY.generated.md`.

    Ensure every in-scope requirement has at least one UAT scenario and every
    UAT scenario references valid requirements.

23. Human scenario packs

    Regenerate:
    `uat/scenario-packs/`

    Verify they match the machine-readable catalog.

24. Automated precheck workflow

    Reconcile `.github/workflows/uat.yml` with Sprint 22/24 workflows.

    Keep one canonical staging/UAT automated precheck.

    It may:
    - verify release identity
    - run regression
    - initialize evidence

    It must not:
    - auto-approve stakeholder signoff
    - receive production credentials
    - silently change the release candidate

25. Generate final report

    Run:
    `scripts/generate-uat-report.py`

    Confirm report counts/statuses match the run JSON.

26. Release decision

    Complete:
    `UAT_RELEASE_DECISION_TEMPLATE.md`

    The decision is tied to the exact image digests.

27. Full regression

    Before final approval, confirm the current release still has valid:
    - Sprint 18 security evidence
    - Sprint 19 QA/E2E evidence
    - Sprint 20 performance evidence
    - Sprint 21 observability evidence
    - Sprint 22 supply-chain/release evidence
    - Sprint 24 staging evidence

28. Do not solve Sprint 25 by:
    - marking skipped scenarios PASS
    - auto-generating human approvals
    - lowering defect severity to pass
    - changing pass threshold mid-run without governance record
    - testing a different image than Sprint 24
    - using production student/staff data
    - claiming WCAG/SRS requirements not present in the source
    - using API tests as the only evidence for usability
    - accepting security/privacy defects with a convenience workaround
    - rebuilding images after acceptance without rerunning UAT

At completion report:
- final SRS requirement mapping
- exact release tag/commit/12 image digests
- UAT environment URL
- participant roles
- Student scenario totals/results
- Teacher scenario totals/results
- Admin scenario totals/results
- CrossRole scenario totals/results
- P0 result
- P1 result
- overall pass rate
- defects by severity/status
- accessibility/usability findings
- Sprint 24 evidence references
- five sign-off decisions
- gate result
- final release decision
- any conditions/deferred MINOR/COSMETIC issues
- confirmation that the exact accepted digests are handed to Sprint 26
