# Sprint 25 Sign-Off Process

Required sign-off roles:

```text
StudentRepresentative
TeacherRepresentative
AdminRepresentative
ProductOwner
ProjectSupervisor
```

## Decisions

Each signer chooses:

```text
APPROVE
APPROVE_WITH_CONDITIONS
REJECT
```

`APPROVE_WITH_CONDITIONS` must list the conditions.

The configured gate treats both APPROVE and APPROVE_WITH_CONDITIONS as present
sign-off, but open BLOCKER/CRITICAL/MAJOR defects and failed mandatory scenarios
still independently fail the gate.

## Student representative

Confirms:

```text
Student workflows are understandable
own data is visible/correct
protected data stays private
assessment/resource/facility flows are acceptable
responsive experience is usable
```

## Teacher representative

Confirms:

```text
assigned classes/rosters are correct
attendance workflow is acceptable
learning-resource publication is usable
assessment authoring/grading is acceptable
unauthorized Admin operations remain unavailable
```

## Admin representative

Confirms:

```text
administrative master data workflow
scheduling/facility operations
reporting/platform workflow
operational usability
```

## Product owner

Confirms:

```text
scope meets acceptance criteria
defect disposition is acceptable
release risk is understood
```

## Project supervisor

Confirms:

```text
evidence exists
requirements traceability is adequate
FYP acceptance package is complete
```

## Recording

Use:

```powershell
python .\scripts\record-uat-signoff.py ...
```

Do not put a person's password, electronic-signature credential, or private
identity document into the UAT JSON.
