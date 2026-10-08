# Sprint 18 Infrastructure Security

## PostgreSQL

Sprint 17 already created one database user per service. Sprint 18 tightens this
further:

```text
REVOKE CONNECT ON DATABASE <db> FROM PUBLIC
GRANT CONNECT ON DATABASE <db> TO <owning-service-user>
REVOKE ALL ON SCHEMA public FROM PUBLIC
```

Application roles remain:

```text
NOSUPERUSER
NOCREATEDB
NOCREATEROLE
NOINHERIT
```

Production services must not receive the PostgreSQL superuser credential.

Backup/restore uses a separate operational credential.

## Object storage

Do not give MinIO/S3 root credentials to application services.

Sprint 18 creates local least-privilege users:

```text
learning_svc  -> learning-resources only
platform_svc  -> platform-imports + platform-exports only
reporting_svc -> report-exports only
```

All buckets remain private.

Suggested service variables:

```text
Learning:
S3_ACCESS_KEY_ID=learning_svc
S3_SECRET_ACCESS_KEY=<LEARNING_S3_SECRET>

Platform:
S3_ACCESS_KEY_ID=platform_svc
S3_SECRET_ACCESS_KEY=<PLATFORM_S3_SECRET>

Reporting:
S3_ACCESS_KEY_ID=reporting_svc
S3_SECRET_ACCESS_KEY=<REPORTING_S3_SECRET>
```

Production should map these concepts to cloud IAM/service accounts rather than
long-lived root credentials.

## RabbitMQ

The Sprint 17 shared `smartedu` broker account is a bootstrap/admin account only
after Sprint 18.

Run:

```powershell
$env:RABBITMQ_BOOTSTRAP_PASSWORD = "<bootstrap-secret>"
$env:RABBITMQ_IDENTITY_PASSWORD = "<secret>"
$env:RABBITMQ_ACADEMIC_PASSWORD = "<secret>"
$env:RABBITMQ_ATTENDANCE_PASSWORD = "<secret>"
$env:RABBITMQ_SCHEDULING_PASSWORD = "<secret>"
$env:RABBITMQ_NOTIFICATION_PASSWORD = "<secret>"
$env:RABBITMQ_FACILITY_PASSWORD = "<secret>"
$env:RABBITMQ_LEARNING_PASSWORD = "<secret>"
$env:RABBITMQ_ASSESSMENT_PASSWORD = "<secret>"
$env:RABBITMQ_REPORTING_PASSWORD = "<secret>"
$env:RABBITMQ_PLATFORM_PASSWORD = "<secret>"

python .\scripts\bootstrap_rabbitmq_security.py
```

Application users are named:

```text
identity_svc
academic_svc
attendance_svc
scheduling_svc
notification_svc
facility_svc
learning_svc
assessment_svc
reporting_svc
platform_svc
```

Each service should use its own AMQP credential.

The management UI/API must not be exposed publicly in production.

## Redis

Use ACLs/managed authentication in staging/production.

At minimum separate:

```text
cache credentials
durable/idempotency/auth-security credentials
```

Identity lockout/rate-limit state should use durable Redis DB 2 or a dedicated
instance/namespace.

Redis must not be publicly reachable.

## TLS

Production:

```text
Browser -> Gateway: HTTPS
PostgreSQL: TLS/sslmode=require or managed equivalent
Redis: rediss:// where supported
RabbitMQ: amqps://
S3: https://
```

Internal TLS termination details depend on deployment environment, but credentials
must never traverse untrusted networks in plaintext.

## Containers

Target controls:

```text
non-root final USER
read-only root filesystem where compatible
cap_drop: ALL
no-new-privileges
bounded tmpfs
no embedded secrets
no public database/broker ports
```

Use:

```powershell
python .\scripts\container_security_audit.py . --strict
```

during CI.
