# Sprint 15 — Complete Admin UX

Sprint 15 replaces the remaining Admin placeholders from Sprint 12 with a
connected administration workspace across Identity, Academic, Scheduling,
Facility, Notification, Reporting, and Platform services.

## Admin experience implemented

### Administration dashboard

- Identity user count
- active enrollment count
- pending Facility bookings
- open Platform support tickets
- attendance percentage
- assessment average
- notification delivery success
- registered/enabled services
- module quick links

### Users & RBAC

Identity Service integration:

- list users
- create Student / Teacher / Admin accounts
- activate / deactivate users
- assign roles
- list roles
- list permissions
- create permission-backed roles

The Sprint 1 Identity contract remains authoritative. Password reset/email
verification endpoints are not invented by Sprint 15.

### Academic setup

Admin workbench for the Sprint 2 academic domain:

- departments
- programs
- academic years
- semesters
- courses
- sections
- Student academic profiles
- Teacher academic profiles
- Student enrollments
- Teacher section assignments

Sprint 2 was implemented locally by Codex and is not present in this packaging
runtime, so the exact path and field names must be reconciled during merge.
Sprint 15 contains a clear frontend adapter boundary in:

`apps/frontend/src/features/admin/admin-api.ts`

Do not solve route mismatches by querying `academic_db` from another service.

### Scheduling

Aligned to Sprint 4's actual Scheduling API:

- list recurring schedules
- create recurring schedules
- cancel schedule
- create CANCELLED occurrence override
- create RESCHEDULED occurrence override
- Teacher, section, room, weekday, time, effective-range, timezone inputs

Scheduling Service remains responsible for conflict prevention and authorization.

### Facilities

Aligned to Sprint 6's actual Facility API:

- create facilities
- configure type/location/capacity/bookability
- enable/disable booking
- list all Admin-visible bookings
- approve booking
- reject booking
- create facility blocks
- cancel facility blocks

Admin decisions continue to use Facility Service conflict/availability rules.

### Notification administration

Aligned to Sprint 5:

- list templates
- create templates
- role campaigns
- section campaigns
- IN_APP delivery
- optional EMAIL delivery
- priority/category
- campaign history/status/recipient count

Teacher section announcements added in Sprint 14 remain separate and restricted.

### Reporting & analytics

Aligned to Sprint 9:

- dashboard overview
- attendance metric rows
- assessment metric rows
- facility metric rows
- notification metric rows
- scheduling metric rows
- enrollment metric rows
- report snapshots
- authenticated CSV export

The Admin UI consumes Reporting Service aggregation. It does not join databases
from the browser or from another service.

### Platform operations

Aligned to Sprint 10:

- service registry
- health/ready sweep
- service latency/status
- settings
- public/private setting visibility
- feature flags
- background jobs
- support-ticket queue
- support assignment/status/priority
- centralized audit trail

## Admin routes

- `/app/admin`
- `/app/admin/users`
- `/app/admin/academic`
- `/app/admin/scheduling`
- `/app/admin/facilities`
- `/app/admin/notifications`
- `/app/admin/reporting`
- `/app/admin/platform`

Shared authenticated routes remain:

- `/app/notifications`
- `/app/profile`

## Gateway-only browser architecture

```text
Admin Browser
     |
     v
Sprint 11 API Gateway
     |
     +--> Identity
     +--> Academic
     +--> Scheduling
     +--> Facility
     +--> Notification
     +--> Reporting
     +--> Platform
```

All Sprint 15 browser code uses Gateway namespaces. It contains no direct
`:8001` through `:8010` service URLs.

## Backend ownership remains unchanged

Sprint 15 does not merge databases or move business rules into the frontend.

- Identity owns accounts/RBAC.
- Academic owns academic master data and enrollment.
- Scheduling owns timetable conflicts and schedule history.
- Facility owns capacity/availability/booking conflicts.
- Notification owns campaign delivery/preferences/retries.
- Reporting owns read-model aggregation.
- Platform owns operational settings, feature flags, support, service registry,
  jobs, and cross-platform audit/search concerns.

## Security

Admin frontend routing is guarded by the `admin` role, but server-side Admin
authorization remains mandatory on every underlying service.

Never rely on frontend route hiding as authorization.

## Production-sensitive controls

Platform settings and feature flags are intentionally presented as JSON objects
because their schemas are platform-specific.

The browser must never display or edit secrets such as:

- JWT signing private keys
- database passwords
- SMTP passwords
- object-storage secret keys
- service-to-service bearer tokens

Secrets remain deployment configuration, not Platform settings.
