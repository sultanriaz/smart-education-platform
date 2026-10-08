# Migration and Seeding Policy

## Alembic

Each service owns its own Alembic history.

Rules:

1. Never import another service's SQLAlchemy metadata.
2. One migration history per service/database.
3. Production application containers do not race each other to run migrations.
4. CI/CD runs one migration job per service before new replicas receive traffic.
5. A migration is tested both `upgrade` and, where supported, downgrade/rollback.
6. Migration drift checks run in CI.
7. Destructive migrations use expand/contract when compatibility is required.

Recommended release sequence:

```text
backup / PITR checkpoint
        ↓
expand migration
        ↓
deploy compatible application
        ↓
backfill if needed
        ↓
verify
        ↓
contract migration in later release
```

## Seeds

Seeds are not migrations.

Seeds must be:

- idempotent
- deterministic
- safe to rerun
- limited to required master/bootstrap data

Examples:

- Identity built-in roles/permissions
- baseline academic master data only when institution-approved
- default notification templates
- platform feature-flag defaults

Do not seed fake demo Students/Teachers into production.

## Rollback

Application rollback must account for schema compatibility.

Do not deploy a schema contraction that prevents the previous application image
from starting until the rollback window has passed.
