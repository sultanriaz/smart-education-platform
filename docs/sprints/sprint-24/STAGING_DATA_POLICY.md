# Staging Data Policy

## No production copy by default

Staging data should be synthetic or specifically approved test data.

Do not copy:

```text
real student records
real employee records
real emails/phone numbers
real attendance history
real assessment answers/grades
production access tokens
production password hashes
production encryption keys
production object files
```

into staging merely to make the environment realistic.

## QA identities

Maintain dedicated:

```text
Student
Teacher
Admin
```

QA identities.

Credentials live in staging secret storage / CI environment secrets.

The repository contains account identifiers/examples only, not passwords.

## Deterministic fixture set

`config/staging/fixture-plan.yaml` defines a small deterministic academic
universe.

The integrated seeder should create it through supported APIs/service-owned
commands rather than cross-service database writes.

The seeder must be:

```text
idempotent
repeatable
safe to reset
clearly marked as staging QA data
```

## Email

Use:

```text
sandbox provider
mail catcher
test recipient domain
```

Never send staging notification campaigns to real university distribution lists.

## Object storage

Use staging-only buckets/prefixes.

Objects should include staging/QA markers.

Lifecycle rules should clean old test uploads and exports.

## Data reset

A reset process may:

```text
delete staging QA records
recreate service databases
re-run migrations
re-seed deterministic fixtures
```

but must operate only on a positively identified staging target.

Reset tooling should require explicit environment confirmation.

## Logging/telemetry

Staging telemetry can be sampled more heavily than production, but the Sprint
18/21 privacy rules still apply.

Do not use staging as an excuse to log passwords/JWTs/assessment answers.
