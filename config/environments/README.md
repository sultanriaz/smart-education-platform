# Environment Separation

Use separate infrastructure, credentials, databases, queues, object-storage
namespaces, and secrets for:

```text
development
staging
production
```

Do not point staging at production databases or buckets.

## Database identity

Each service has one database and one least-privilege login:

| Service | Database | Login |
|---|---|---|
| Identity | identity_db | identity_svc |
| Academic | academic_db | academic_svc |
| Attendance | attendance_db | attendance_svc |
| Scheduling | scheduling_db | scheduling_svc |
| Notification | notification_db | notification_svc |
| Facility | facility_db | facility_svc |
| Learning | learning_db | learning_svc |
| Assessment | assessment_db | assessment_svc |
| Reporting | reporting_db | reporting_svc |
| Platform | platform_db | platform_svc |

Local development may place these logical databases in one PostgreSQL container.
Production can place them on one managed cluster or separate clusters depending
on scale, but credentials and ownership remain service-specific.

## Secret rules

Secret values belong in the deployment secret store, not:

- Git
- `.env.*.example`
- frontend Vite variables
- Platform settings
- Docker images
- logs
- documentation screenshots

## Production public ports

The local infrastructure Compose exposes ports for developer convenience.

Production should not publicly expose:

```text
PostgreSQL
Redis
RabbitMQ AMQP
RabbitMQ management UI
MinIO/S3 admin console
```

Only application ingress/Gateway belongs on the public edge.
