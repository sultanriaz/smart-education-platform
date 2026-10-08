# Sprint 25 Accessibility & Usability Acceptance

The source SRS is known to require responsive desktop/mobile behavior. The
project's exact formal accessibility standard should be reconciled with the
final SRS; Sprint 25 therefore uses a practical accessibility baseline without
claiming an unsupported SRS standard.

## Keyboard

For representative Student, Teacher, and Admin flows verify:

```text
all required controls keyboard reachable
logical focus order
visible focus
no keyboard trap
dialogs/menus can be exited
submit/cancel actions reachable
```

## Labels and names

Verify:

```text
inputs have understandable labels
buttons/links have meaningful accessible names
required fields are communicated
validation errors identify the affected field
```

## Error handling

User-facing errors should:

```text
avoid stack traces
avoid secrets/internal tokens
state what failed
provide a reasonable next action where possible
```

## Responsive behavior

Test at least:

```text
desktop
tablet-like width
mobile-like width
```

Core tasks must not lose required controls or require impractical horizontal
scrolling.

## Visual clarity

Check:

```text
readable text
usable form spacing
status/badge meaning not encoded only by color where possible
clear destructive-action confirmation
empty/loading/error states understandable
```

## Assistive technology smoke

Where available, use browser accessibility tree and one common screen-reader
smoke pass for:

```text
login
navigation
one form
one data/detail page
```

This is not a substitute for a formal accessibility audit if one is required by
the institution.

## Evidence

Capture:

```text
browser/device/viewport
scenario ID
issue description
screenshot/video where useful
accessibility-tool output where used
```
