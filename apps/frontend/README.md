# Smart Education Platform Frontend — Sprint 12

React + TypeScript + Tailwind frontend foundation for the Smart Education
Platform. Sprint 12 establishes the shared architecture; detailed Student,
Teacher, and Admin domain screens are intentionally left for Sprints 13–15.

## Stack

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- React Hook Form
- Zod
- Vitest
- Testing Library

## Architecture

The browser communicates with the Sprint 11 API Gateway only.

```text
Browser
  |
  v
API Gateway :8080
  |
  +--> Identity
  +--> Academic
  +--> Attendance
  +--> Scheduling
  +--> Notification
  +--> Facility
  +--> Learning
  +--> Assessment
  +--> Reporting
  +--> Platform
```

Gateway namespaces are centralized in `src/lib/service-paths.ts`.

## Authentication foundation

Implemented:

- login
- public Student registration
- current-user restoration
- access-token bearer requests
- single-flight refresh after 401
- refresh-token rotation compatibility
- logout
- protected routes
- Student / Teacher / Admin RBAC navigation

The package accepts common snake_case and camelCase Identity token fields. The
merge pass must reconcile the exact Sprint 1 contract.

### Current token storage

For compatibility with the original JSON token API, access and refresh tokens are
stored in `sessionStorage`.

For production hardening, prefer:
- short-lived access token in memory
- refresh token in an HttpOnly, Secure, SameSite cookie
- CSRF-aware refresh/logout behavior

Only switch to that model if the real Identity Service supports it.

## Runtime configuration

The frontend image does not need to be rebuilt just to change the gateway URL.

Docker generates `/runtime-config.js` from:
- `API_BASE_URL`
- `APP_NAME`

Default gateway: `http://localhost:8080`.

## Routes

Public:
- `/login`
- `/register`
- `/forbidden`

Common authenticated:
- `/app`
- `/app/profile`
- `/app/notifications`

Student:
- `/app/student`
- `/app/student/attendance`
- `/app/student/timetable`
- `/app/student/learning`
- `/app/student/assessments`
- `/app/student/facilities`

Teacher:
- `/app/teacher`
- `/app/teacher/attendance`
- `/app/teacher/timetable`
- `/app/teacher/learning`
- `/app/teacher/assessments`

Admin:
- `/app/admin`
- `/app/admin/users`
- `/app/admin/academic`
- `/app/admin/scheduling`
- `/app/admin/facilities`
- `/app/admin/reporting`
- `/app/admin/platform`

## Development

```powershell
cd apps\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`.

For Vite development, Sprint 11 gateway should allow:
`http://localhost:5173`.

## Verification

```powershell
npm run typecheck
npm run lint
npm run test
npm run build
```

## Docker

From repository root:

```powershell
docker compose -f .\docker-compose.frontend.yml up -d --build
```

Open `http://localhost:3000`.

For Dockerized frontend testing, gateway CORS should allow:
`http://localhost:3000`.

## Accessibility baseline

Included:
- skip link
- semantic navigation
- labelled forms
- associated validation errors
- keyboard-visible focus
- aria-live toast/status areas
- responsive navigation
- semantic headings

## Next work

- Sprint 13: Student UX
- Sprint 14: Teacher UX
- Sprint 15: Admin UX
