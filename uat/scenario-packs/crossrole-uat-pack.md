# CrossRole UAT Scenario Pack

Release tag: ____________________  
Commit SHA: ____________________  
Staging/UAT URL: ____________________  
Execution date: ____________________

Use the structured CLI run record as the source of truth for final gate evaluation. This document is a human-friendly execution worksheet.

## UAT-X-001 — Role isolation across Student, Teacher, and Admin

**Role:** CrossRole  
**Domain:** Security  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-RBAC, REQ-PRIVACY

### Steps

1. Authenticate as each role in turn.
2. Attempt at least one forbidden action from each lower-privilege role.

### Expected results

- Each role can perform intended work only.
- Server-side authorization rejects forbidden operations.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-002 — Session inactivity and re-authentication behavior

**Role:** CrossRole  
**Domain:** Identity  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-IDENTITY-SESSION

### Steps

1. Authenticate with a QA account.
2. Leave the session inactive for the configured inactivity period or use approved test acceleration.
3. Attempt a protected action.

### Expected results

- Session handling matches the final 10-minute inactivity requirement/implementation.
- Expired session cannot silently continue privileged work.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-003 — No cross-user protected data exposure

**Role:** CrossRole  
**Domain:** Security  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-PRIVACY, REQ-RBAC

### Steps

1. Capture a protected resource identifier from QA user A.
2. Attempt access as QA user B without required relationship/role.

### Expected results

- Request is denied or returns no protected data.
- UI does not reveal inaccessible data.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-004 — General performance acceptance evidence

**Role:** CrossRole  
**Domain:** Performance  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-PERF-GENERAL, REQ-CONCURRENCY

### Steps

1. Review latest Sprint 20 staging performance evidence for the exact release candidate.

### Expected results

- Required normal p95 and concurrency evidence exists for the release/environment or is explicitly blocked from promotion.
- Evidence references exact release tag/commit.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-005 — Availability and readiness behavior

**Role:** CrossRole  
**Domain:** Reliability  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-AVAILABILITY

### Steps

1. Review Sprint 21 SLO/availability evidence and staging pod-failure/rolling-update drills.
2. Confirm readiness removes unhealthy instances.

### Expected results

- Release has no unresolved availability blocker.
- Application remains usable through the accepted failure drills.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-006 — Recovery evidence review

**Role:** CrossRole  
**Domain:** Reliability  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-RECOVERY

### Steps

1. Review Sprint 24 database restore drill.
2. Review object-storage recovery drill.
3. Review release redeploy/secret recovery evidence.

### Expected results

- Recovery evidence is complete and internally consistent.
- Failed recovery drill blocks promotion.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-007 — Keyboard-only core navigation

**Role:** CrossRole  
**Domain:** Accessibility  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-ACCESSIBILITY

### Steps

1. Use keyboard only through login and one core workflow for each role.
2. Inspect focus visibility and logical order.

### Expected results

- All required controls are reachable.
- Visible focus is maintained.
- No keyboard trap blocks completion.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-008 — Labels, errors, and accessible names

**Role:** CrossRole  
**Domain:** Accessibility  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-ACCESSIBILITY

### Steps

1. Trigger representative validation errors.
2. Inspect form labels, error association, button/link accessible names using browser accessibility tooling.

### Expected results

- Required inputs have understandable labels.
- Errors identify the affected field/action.
- Controls have meaningful names.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-009 — Responsive core workflows

**Role:** CrossRole  
**Domain:** Usability  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-RESPONSIVE

### Steps

1. Run representative Student, Teacher, and Admin tasks at desktop width.
2. Repeat critical navigation at mobile/tablet width where supported.

### Expected results

- Core tasks remain usable.
- No required control becomes unreachable.
- Layout changes do not change authorization behavior.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-X-010 — User-facing failure messages are actionable

**Role:** CrossRole  
**Domain:** Usability  
**Priority:** P2  
**Execution:** hybrid  
**Requirements:** REQ-RESPONSIVE

### Steps

1. Trigger a safe validation error.
2. Trigger/observe a safe unavailable-dependency scenario in staging if planned.
3. Review displayed error text.

### Expected results

- Messages explain what happened without exposing stack traces/secrets.
- User has a reasonable next action or retry path.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---
