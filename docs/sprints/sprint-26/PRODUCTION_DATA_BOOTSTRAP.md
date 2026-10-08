# Production Data Bootstrap

Production bootstrap must be explicit and non-destructive.

## Allowed examples

Depending on final product requirements:

```text
baseline permissions
roles
required platform configuration
institution-owned academic master data import
initial approved Admin account/bootstrap path
```

## Rules

Bootstrap must:

```text
be idempotent where practical
be auditable
use supported APIs/service-owned commands
respect service DB ownership
avoid cross-service direct DB writes
avoid overwriting existing production data
```

## Admin/bootstrap credentials

Never commit an initial production password.

Use:

```text
one-time secret
forced password/reset flow
approved identity bootstrap mechanism
```

and rotate/remove bootstrap credentials immediately after use.

## Academic data

Real production academic data import must have:

```text
source owner
validation
dry run
row/error counts
rollback/correction plan
privacy review
```

Do not use Sprint 24 QA fixture data as production seed data.
