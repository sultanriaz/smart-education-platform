# Sprint 22 Database Migration Release Policy

Each service owns its Alembic history and database. CI requires one head and schema-drift checks. Release manifests record which components changed migration files.

Staging deployment performs an approved backup before migration, then runs `alembic upgrade head` using the release image for that service. Database downgrades are never automatic.

Production-compatible migration design should use expand/migrate/contract where schema compatibility spans old/new app versions. Prefer additive nullable columns/tables first, deploy code that tolerates both schemas, backfill asynchronously, then remove legacy structures only in a later release.

Rollback of application images is safe only when the current schema remains compatible. Otherwise use forward-fix. Any reversible downgrade must be explicitly implemented, tested on realistic backup data, and approved.
