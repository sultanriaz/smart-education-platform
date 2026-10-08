# Sprint 15 Verification

Actual checks executed in the packaging environment:

## frontend_typecheck

Exit code: `0`

```text
Merged Sprint 12 + Sprint 13 + Sprint 14 + Sprint 15 frontend sources:
tsc --noEmit --pretty false
PASS
```

## route_coverage

Exit code: `0`

```text
Admin dashboard      PASS
Users & RBAC         PASS
Academic setup       PASS
Scheduling           PASS
Facilities           PASS
Notifications        PASS
Reporting            PASS
Platform operations  PASS
Student routes preserved
Teacher routes preserved
```

## gateway_only

Exit code: `0`

```text
direct_service_port_hits=[]
```

## known_contract_paths

Exit code: `0`

The Sprint 15 frontend adapter contains the known contracts from the already
generated services:

```text
Identity users                          PASS
Scheduling schedules                    PASS
Notification Admin templates            PASS
Notification Admin campaigns            PASS
Facility facilities                     PASS
Facility bookings                       PASS
Facility blocks                         PASS
Reporting dashboard overview            PASS
Platform service registry               PASS
```

The Academic contract is intentionally excluded from this "known contract" check
because Sprint 2 was implemented locally by Codex and its source is not available
inside the packaging runtime. It must be reconciled against the actual repository
OpenAPI during merge.

## bom_scan

Exit code: `0`

```text
BOM files: []
```

## Not claimed as verified here

The packaging environment does not contain the user's complete merged local
repository, npm dependency tree, Docker runtime, or Sprint 2/3 source.

Therefore these remain repository-integration checks:

- `npm install`
- `npm run lint`
- `npm run test`
- `npm run build`
- frontend Docker build
- live Identity Admin workflow
- live Academic Admin CRUD/withdraw/unassign flow
- live Scheduling conflict behavior
- live Facility approval/block behavior
- live Notification campaign delivery
- live Reporting snapshot/CSV export
- live Platform health/settings/features/jobs/support/audit
- Admin browser E2E
- Student/Teacher regression E2E
- Gateway/CORS/deep-link runtime tests

The merge pass must run the full checklist in `SPRINT_15_INTEGRATION.md`.
