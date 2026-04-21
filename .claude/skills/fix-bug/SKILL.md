---
name: fix-bug
description: Reproduce, isolate, fix, and validate a bug with minimal change surface
---

# Fix a bug

Use this skill when the task is a bugfix rather than a new feature.

## Goals

- Reproduce the bug if practical
- Isolate the smallest responsible code path
- Fix with minimal surface area
- Add regression protection

## Workflow

1. Clarify the failure.
   - Capture the observed behavior, expected behavior, and likely entry point.
   - Inspect the narrowest relevant files first.

2. Reproduce.
   - Prefer a failing test when practical.
   - If no test harness fits, produce a minimal reasoning-based reproduction path.

3. Isolate the cause.
   - Follow existing control flow and local patterns.
   - Avoid broad refactors while debugging.

4. Implement the smallest correct fix.
   - Preserve existing interfaces unless the bug requires changing them.
   - Avoid opportunistic cleanup unrelated to the defect.

5. Add regression coverage.
   - Add or update the narrowest meaningful test.
   - Prefer targeted tests before running wider suites.

6. Validate.
   - Run the affected test(s).
   - Run lint/format checks if Python files changed.
   - Expand validation only as needed.

7. Report.
   - State root cause
   - State what changed
   - State what was validated
   - State any residual risk or unverified edge case

## Notes

- Do not claim the bug is fixed without saying how it was validated.
- Prefer local, reversible changes over architectural rewrites.