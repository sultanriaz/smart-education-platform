# Academic Service API contract, version 1

Base path: `/api/v1`; local base URL: `http://localhost:8002`.
Interactive schemas and request examples are at `/docs`; JSON OpenAPI is at
`/openapi.json`. Health endpoints `/health` and `/ready` are public.

## Authentication and authorization

Supply `Authorization: Bearer <access_token>` using the
[Identity authentication contract](identity-authentication.md). Academic pins
RS256, requires `typ=at+jwt`, a nonempty trusted `kid`, `type=access`, the configured
issuer and access audience, UUID `sub`, string-array `roles`, nonempty `jti`, and
valid required `iat`, `nbf`, and `exp` NumericDate claims. The default clock
tolerance is five seconds. Role names are the contract's exact lowercase names.

JWT validation runs in synchronous FastAPI dependencies. Public JWKS sets are
cached for five minutes with a five-second fetch timeout; individual keys are not
cached indefinitely. JWT `jku`/`x5u` headers never select the trusted JWKS URL.
Missing/invalid tokens return 401 with `WWW-Authenticate: Bearer`; forbidden
operations return 403; unavailable key discovery returns 503. Signature validation
never falls back to unverified claims.

| Resource | Administrator | Teacher |
| --- | --- | --- |
| Departments, programs, academic years, semesters, courses | Full CRUD | Read |
| Student academic profiles | Full CRUD | No direct access |
| Teacher academic profiles | Full CRUD | Own active profile through `/teacher-profiles/me` |
| Sections | Full CRUD | Read own actively assigned sections |
| Enrollments | Create/read/change status/delete | No direct access |
| Teacher assignments | Create/read/activate/deactivate/delete | Read own active assignments |
| Section rosters | Read any section | Read own actively assigned sections |

Student-role tokens have no Academic API access in Sprint 2. All mutations require
`admin`, including enrollment changes and teacher assignments. Teacher resource
access requires a local active teacher profile linked to JWT `sub`, plus a local
active assignment; knowing a section UUID is insufficient. Academic assignment
revocation affects the next request. Identity role/account changes take up to the
access token lifetime plus clock tolerance, as defined by Identity's offline-token
contract. This service does not call Identity for per-request account freshness.

## Routes

Each of these collections supports `POST`, `GET`, `GET /{id}`, `PUT /{id}`, and
`DELETE /{id}`:

- `/departments`
- `/programs`
- `/academic-years`
- `/semesters`
- `/courses`
- `/sections`
- `/student-profiles`
- `/teacher-profiles`

`PUT` supplies a full replacement body; IDs and timestamps are response-only.
List endpoints use `limit` (default 50, maximum 100) and `offset` (default 0).
Lists return arrays ordered by creation timestamp and UUID. Creation returns 201,
replacement returns 200, and deletion returns 204. Request fields not in the
schema are rejected.

| Route | Behavior |
| --- | --- |
| `GET /teacher-profiles/me` | Caller’s active academic teacher profile |
| `POST /enrollments` | Enroll `student_profile_id` in `section_id` |
| `GET /enrollments` | Admin list; optional `student_profile_id` and `section_id` filters |
| `GET /enrollments/{id}` | Admin enrollment detail |
| `PATCH /enrollments/{id}` | Set `status`: `enrolled`, `dropped`, or `completed` |
| `DELETE /enrollments/{id}` | Admin removal |
| `POST /teacher-assignments` | Assign `teacher_profile_id` to `section_id` |
| `GET /teacher-assignments` | All assignments for admin, own active assignments for teacher |
| `GET /teacher-assignments/{id}` | Assignment detail within caller’s scope |
| `PATCH /teacher-assignments/{id}` | Set `is_active` |
| `DELETE /teacher-assignments/{id}` | Admin removal |
| `GET /sections/{id}/roster` | Paginated active enrollment roster |

The roster response includes `section_id`, `total` active enrollments, `limit`,
`offset`, and `students`. Each entry has `enrollment_id`, `student_profile_id`,
`external_user_id`, and `student_number`. Dropped/completed enrollments are excluded.

## Model relationships and identifiers

Academic owns ten tables: departments, programs, academic_years, semesters,
courses, sections, student_academic_profiles, teacher_academic_profiles,
enrollments, and teacher_assignments. Rosters are a projection of enrollments.
Every record has UUID `id`, `created_at`, and `updated_at`.

Programs belong to departments and define `duration_semesters`. Courses belong
to a program and define positive `credits` and curriculum `semester_number`.
Semesters belong to academic years, with a positive `number` and dates inside
that year. Semester `number` identifies a term within a year; a course’s
`semester_number` is its position in a program curriculum.

Sections connect a course to an offered semester and define a code and positive
capacity. Student profiles store `external_user_id`, `student_number`, program,
admission year, current curriculum semester, and active status. Teacher profiles
store `external_user_id`, `employee_number`, department, designation, and active
status. Enrollment/assignment requests reference Academic profile IDs, not user IDs.

External UUIDs are opaque Identity references: no cross-database foreign keys,
Identity ORM imports, credentials, or copied Identity roles. Provisioning workflows
must obtain real user UUIDs from Identity before the admin creates these profiles;
Academic does not verify existence or role through Identity tables or network calls.

## Domain constraints

- Department/program/year/course codes are globally unique within their table.
  Codes are trimmed and case-sensitive. A semester number is unique within a year;
  a section code is unique per course and offered semester.
- User UUID and student/employee number are unique within each profile table.
  The same external user can hold both academic profile types.
- Parent foreign keys, external user UUIDs, semester term numbers, and course
  curriculum semester numbers are immutable after creation. Corrections require
  creating a new record and resolving dependencies explicitly.
- Dates must satisfy `ends_on > starts_on`. Year date changes cannot exclude
  existing semesters. Program duration changes cannot exclude existing courses or
  students. Missing references return 404, invalid bodies return 422, and business
  conflicts/duplicate records/referenced deletion attempts return 409.
- Students and sections must be active for enrollment. Student/course programs
  and curriculum semesters must match; a section cannot precede the student’s
  admission year. A student may hold one non-dropped enrollment for a course in
  an offered semester, even across different sections.
- A student/section pair remains unique after dropping. Restore the existing
  enrollment with `PATCH` instead of posting another one. Restoring repeats all
  eligibility/capacity checks. `enrolled` can become `dropped` or `completed`;
  `dropped` can become `enrolled`; `completed` is final for status changes.
- Only `enrolled` records consume capacity. Section capacity cannot be reduced
  below current enrollment. Resolve active enrollments before changing a student’s
  current semester or deactivating the student. Admin deletion is explicit and
  permitted for enrollment records, including historical records.
- Teachers/sections must be active for assignment, and the teacher department
  must match the course program’s department. Teacher/section pairs are unique;
  restore inactive assignments with `PATCH`. Resolve active assignments before
  deactivating a teacher profile.
- Foreign keys prevent deleting referenced catalog/profile records; there are no
  cascading academic deletes. Services commit/rollback; repositories only flush.
  PostgreSQL section locks serialize capacity mutations, and student locks prevent
  concurrent enrollment into two sections for the same course/semester. Database
  and lock timeout failures return 503 so clients can retry.
