# Admin UAT Scenario Pack

Release tag: ____________________  
Commit SHA: ____________________  
Staging/UAT URL: ____________________  
Execution date: ____________________

Use the structured CLI run record as the source of truth for final gate evaluation. This document is a human-friendly execution worksheet.

## UAT-ADM-001 — Admin login and administrative workspace

**Role:** Admin  
**Domain:** Identity  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-IDENTITY-AUTH, REQ-RBAC

### Steps

1. Authenticate with Admin QA account.
2. Open Admin dashboard/navigation.

### Expected results

- Admin workspace loads.
- Administrative capabilities required for UAT are available.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-002 — Manage academic master data

**Role:** Admin  
**Domain:** Academic  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ACADEMIC-MASTER

### Steps

1. Create or update a QA academic entity permitted by the final API.
2. Create/update a QA course/section.
3. Review resulting data.

### Expected results

- Valid changes persist.
- Uniqueness/relationship constraints are enforced.
- No production-like unmarked data is created.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-003 — Manage users and roles safely

**Role:** Admin  
**Domain:** Identity  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-RBAC, REQ-IDENTITY-AUTH

### Steps

1. Open Admin user management.
2. Inspect a QA user.
3. Perform one allowed status/role administration action.
4. Verify effect with the QA identity.

### Expected results

- Only Admin can perform the action.
- Change takes effect consistently.
- Audit/security controls remain intact.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-004 — Create schedule and reject conflict

**Role:** Admin  
**Domain:** Scheduling  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-SCHEDULING

### Steps

1. Create a valid QA schedule occurrence/recurrence.
2. Attempt a conflicting schedule for the same protected resource/time.

### Expected results

- Valid schedule is accepted.
- Conflict is rejected according to backend concurrency/conflict rules.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-005 — Facility approval lifecycle

**Role:** Admin  
**Domain:** Facility  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-FACILITY

### Steps

1. Open pending QA booking.
2. Approve or reject according to test case.
3. Inspect booking history/state.

### Expected results

- Lifecycle transition is valid and persisted.
- History/audit shows the administrative decision.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-006 — Reporting dashboard reflects staged events

**Role:** Admin  
**Domain:** Reporting  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-REPORTING

### Steps

1. Generate/confirm QA attendance or assessment events.
2. Open reporting dashboard/metrics.
3. Compare displayed projection to known QA fixture/event.

### Expected results

- Reporting reflects the event-driven projection accurately enough for the acceptance case.
- No synchronous cross-service DB coupling is required for the dashboard.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-007 — Export an authorized report

**Role:** Admin  
**Domain:** Reporting  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-REPORTING, REQ-PRIVACY

### Steps

1. Request a supported CSV/report export.
2. Open downloaded output.
3. Check expected QA rows and absence of unrelated protected data.

### Expected results

- Export completes.
- Columns/rows are usable.
- Authorization scope is preserved.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-008 — Platform settings or feature flag management

**Role:** Admin  
**Domain:** Platform  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-PLATFORM, REQ-RBAC

### Steps

1. Open Platform administration.
2. Modify an approved QA-only setting/feature flag.
3. Verify resulting state.

### Expected results

- Admin-only change succeeds.
- Setting is not used to store secrets.
- Audit/change history is available where implemented.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-009 — Support/audit operational visibility

**Role:** Admin  
**Domain:** Platform  
**Priority:** P2  
**Execution:** hybrid  
**Requirements:** REQ-PLATFORM

### Steps

1. Open support/audit area.
2. Inspect a QA support ticket or operational audit entry.

### Expected results

- Expected QA operational information is visible to Admin.
- Sensitive secret material is not exposed.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-ADM-010 — Internal Gateway routes remain blocked

**Role:** Admin  
**Domain:** Security  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-RBAC, REQ-PRIVACY

### Steps

1. Attempt a known namespaced `/internal/` route through the public Gateway using approved test tooling.

### Expected results

- Public Gateway blocks the internal service endpoint.
- Internal service token/API is not exposed to normal browser users.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---
