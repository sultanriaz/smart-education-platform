# Operations Ownership

Before production, every operational domain must have a named owner.

## Application

Owner responsibilities:

```text
release validation
migration coordination
application incidents
service-level defects
rollback compatibility
```

## Infrastructure

Owner responsibilities:

```text
Kubernetes
Ingress/load balancer
DNS/TLS
PostgreSQL
Redis
RabbitMQ
object storage
backups
capacity
```

## Security

Owner responsibilities:

```text
secrets
access control
incident escalation
vulnerability/supply-chain review
credential/key rotation
network exposure
```

## Product/UAT

Owner responsibilities:

```text
launch scope
user communications
known issue decisions
UAT acceptance
business impact assessment
```

## Support

Define:

```text
how users report an issue
who triages it
severity definitions
expected acknowledgement
escalation path
```

## Coverage

For the launch window record:

```text
primary owner
backup owner
contact channel
coverage start
coverage end
```

Do not rely on one individual being continuously available.
