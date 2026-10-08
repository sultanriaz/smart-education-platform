# Sprint 05 Integration — Notification Service

Extract this pack into the repository root. It adds:

- `services/notification-service/`
- `docker-compose.notification.yml`
- `.github/workflows/notification-service-ci.yml`

## Required merge checks

1. Preserve service/database boundaries. Notification Service must never import another service's ORM/domain package or access another service DB.
2. Compare the Identity JWT/JWKS contract against Academic/Scheduling and align config names only if necessary.
3. Verify Identity endpoints used by `app/clients/identity.py` (`/api/v1/users`, `/api/v1/users/{id}`). Adapt the client if the live contract differs.
4. Verify Academic roster endpoint and set `ACADEMIC_SECTION_ROSTER_PATH_TEMPLATE` accordingly.
5. Wire upstream transactional outbox relays to `POST /api/v1/internal/events`. Do not poll upstream DBs from Notification Service.
6. Ensure schedule occurrence events expose section/teacher targeting context. A non-breaking patch to Sprint 4's occurrence outbox payload is acceptable.
7. Ensure low-attendance events expose `student_user_id` or explicit event targets.
8. Use real secrets for `INTERNAL_EVENT_TOKEN` and service tokens; never commit them.
9. Run migrations and the complete test suite before commit.

## Local ports

- Notification API: `8005`
- Notification PostgreSQL: `${NOTIFICATION_DB_PORT:-5438}`
- Notification Redis: `${NOTIFICATION_REDIS_PORT:-6380}`

## Suggested commit

```text
feat(notification): add notification delivery event inbox and preferences service
```

Suggested tag:

```text
sprint-05-notification
```
