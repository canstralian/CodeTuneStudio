# SYSTEM.md

## Execution Model

Code execution occurs within controlled, environment-specific limits. Execution is not fully sandboxed or isolated.

### Controlled:
- Process invocation
- Resource limits
- Subprocess scope

### Not Controlled:
- OS-level isolation
- Container or user boundary enforcement

## Plugin Contract

Plugins do not define transformations. They propose candidates. Governance determines what survives.

### Rules for Plugins

- **Must Not:**
  - Write directly to final output.
  - Bypass validation layers.
- **May Only:**
  - Emit proposed transformations.
  - Emit confidence metadata.

## System Contract

### Guarantees:
1. Failures are localizable and actionable.
2. Transformations are verifiable before acceptance.
3. Explanations correspond to validated outcomes.

### Non-Guarantees:
1. Full execution isolation.
2. Behavioral equivalence across non-compliant plugins.
3. Model-level determinism.

### Implication:
- Anything violating a guarantee is a bug.
- Anything violating a non-guarantee is expected behavior.

## Known Failure Classes

### Explanation Drift
- **Issue:** Explanations may diverge from applied transformations when generated independently.
- **Design Intent:**
  - Explanations should be derived from validated transformation deltas wherever feasible.