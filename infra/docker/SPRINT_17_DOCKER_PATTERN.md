# Sprint 17 Shared Infrastructure Package in Service Images

Use the repository root as Docker build context.

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY libs/python/smartedu_contracts /tmp/smartedu_contracts
RUN pip install --no-cache-dir /tmp/smartedu_contracts

COPY libs/python/smartedu_infra /tmp/smartedu_infra
RUN pip install --no-cache-dir "/tmp/smartedu_infra[postgres]"

COPY services/<service>/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/<service>/app ./app
```

Compose:

```yaml
build:
  context: .
  dockerfile: services/<service>/Dockerfile

networks:
  - smartedu-backend
```

Do not use host-mount imports for production.

## Database URLs inside Docker

Use the infrastructure network hostname:

```text
postgresql+psycopg://academic_svc:<secret>@infra-postgres:5432/academic_db
```

not `localhost`.

## Redis

Cache:

```text
redis://redis-cache:6379/0
```

Durable/idempotency:

```text
redis://redis-durable:6379/0
```

Keep volatile cache workload separate from durable idempotency state.

## RabbitMQ

```text
amqp://<user>:<secret>@rabbitmq:5672/smartedu
```

## Object storage

```text
S3_ENDPOINT_URL=http://minio:9000
```

All buckets are private. Use application-authorized downloads or short-lived
presigned URLs.
