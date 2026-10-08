# Sprint 21 Logging Policy

## Format

Application logs are structured JSON with:

```text
timestamp
level
logger
message
service
environment
service_version
request_id
correlation_id
trace_id
span_id
fields
```

## Required behavior

Every user-facing request should be traceable through:

```text
Gateway request_id
correlation_id
service logs
distributed trace
event correlation_id where asynchronous work occurs
```

## Sensitive data

Never log:

```text
password
Authorization header
Cookie / Set-Cookie
access token
refresh token
reset token
email-verification token
private key
database password
RabbitMQ password
S3 secret
security pepper
encrypted security payload
```

The shared formatter redacts common sensitive keys, but callers must still avoid
placing secrets in free-form log messages.

## User data

Do not log complete educational records just because a serializer makes it easy.

Prefer:

```text
record UUID
operation
result
count
reason code
```

over full request/response bodies.

## Levels

```text
DEBUG   local diagnostic detail; normally disabled in production
INFO    normal lifecycle/request/business-operation summaries
WARNING recoverable degradation, retry, unusual state
ERROR   failed operation requiring attention
CRITICAL severe platform condition requiring immediate response
```

Expected authorization denials generally do not need ERROR severity.

## Stack traces

Log stack traces for unexpected failures.

Do not duplicate the same exception at every layer. Record it once at the layer
that owns the failure boundary, while traces capture propagation.

## Retention

Bundled Loki development retention is 7 days.

Production retention must follow institutional/privacy requirements and storage
cost. Do not increase retention by default without deciding what educational
data the logs may contain.
