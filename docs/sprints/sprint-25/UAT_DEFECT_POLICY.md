# Sprint 25 UAT Defect Policy

The machine-readable policy is:

```text
config/uat/defect-policy.yaml
```

## BLOCKER

UAT cannot continue or the release is unusable for a core role/workflow.

Examples:

```text
role cannot log in
application cannot load
migration prevents use
data corruption
```

Release gate:

```text
must be closed
```

## CRITICAL

Serious security, authorization, privacy, data-integrity, or core workflow
failure with no acceptable workaround.

Examples:

```text
Student sees another Student's result
Teacher performs Admin action
assessment answer key exposed
protected internal API exposed
```

Release gate:

```text
must be closed
```

## MAJOR

Important workflow materially fails.

Examples:

```text
Teacher cannot finalize attendance
Admin cannot produce required report
facility conflict rule fails
published learning resource cannot be accessed
```

Default release gate:

```text
must be closed
```

## MINOR

Localized defect where the workflow remains usable and safe.

May be deferred only with:

```text
owner
target release/date
documented impact
```

## COSMETIC

Presentation-only issue that does not affect:

```text
correctness
usability
accessibility
security
data integrity
```

May be deferred.

A focus indicator/accessibility failure is not automatically "cosmetic."

## Status

```text
OPEN
IN_PROGRESS
FIXED
RETEST
CLOSED
DEFERRED
```

Only `CLOSED` means verified resolved.

`FIXED` still requires UAT retest where the defect affected acceptance.

## Workarounds

Workarounds are documented for testers and business evaluation.

They do not reduce severity automatically.

Security or data-integrity defects should not be waived merely because a careful
user can avoid triggering them.
