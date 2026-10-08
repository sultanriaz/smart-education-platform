# Backup and Restore Architecture

The original SRS requires no normal-operation data loss and recovery within a
very small window. A nightly backup alone cannot satisfy that expectation.

Production therefore needs HA plus continuous or near-continuous recovery
mechanisms.

## PostgreSQL

Required production capabilities:

```text
HA failover
continuous WAL archiving / PITR
automated snapshots
encrypted backups
retention policy
restore testing
```

Recommended recovery evidence:

```text
node failure -> managed/cluster failover
operator error -> PITR
major disaster -> restored isolated database/cluster
```

Keep backups logically aligned with database-per-service ownership even when one
physical PostgreSQL cluster hosts multiple service databases.

## Redis

`redis-cache` does not need backup for correctness.

`redis-durable` requires persistence/HA appropriate to its real use:

```text
AOF and/or managed persistence
replication
snapshots where supported
```

Correctness must still be designed so Redis is not the sole permanent business
record.

## RabbitMQ

Use durable/quorum queue settings from Sprint 17.

Back up broker definitions/configuration where the broker product supports it.

Transactional outboxes allow source services to republish events after broker
recovery.

Do not treat a RabbitMQ disk snapshot as the only business-data backup.

## Object storage

Enable:

```text
versioning
server-side encryption
retention/lifecycle
delete protection where appropriate
replication where required by the final risk model
```

Learning resources and exports should be restorable without database/object
metadata divergence.

## Kubernetes configuration

Git + Sprint 22 release manifests are the desired-state backup for stateless
application manifests.

Back up only cluster objects that are not reproducible from Git/secret manager.

## Restore drills

A backup is not considered operationally useful until a restore drill succeeds.

At minimum staging should rehearse:

```text
PostgreSQL PITR/restore
object-version recovery
release manifest redeploy
secret recovery/rotation
```

Record elapsed recovery time and any manual steps.

Sprint 24 will exercise these procedures in staging.
