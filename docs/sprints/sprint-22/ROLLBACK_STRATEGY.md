# Sprint 22 Rollback Strategy

Application rollback means redeploying a previously verified release manifest by immutable image digest. Do not rebuild an old source tag because dependencies/base images may have changed.

Database rollback is separate. The default is forward-fix. The staging rollback workflow requires an explicit schema-compatibility confirmation and never executes `alembic downgrade` automatically.

Before rollback, check: current migration state, backward compatibility, queued event schema compatibility, Redis/cache format, RabbitMQ consumer compatibility, and object-storage metadata assumptions. After rollback, run health/readiness plus Student/Teacher/Admin smoke paths.
