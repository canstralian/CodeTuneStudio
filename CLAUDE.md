CLAUDE.md

0. Control Hierarchy

1. User instructions
2. This document
3. Repository conventions

Never invert this order.

⸻

1. Execution Model

Operate as a stateful code agent with constrained I/O.

Core loop

1. Read → identify relevant files
2. Plan → minimal viable change
3. Act → targeted edits only
4. Validate → test or reason-check
5. Report → concise, no padding

Do not skip steps.

⸻

2. File Interaction Rules

Reading

* Read before writing.
* Do not re-read unchanged files.
* Avoid files >100KB unless required.
* Expand scope only if necessary to resolve uncertainty.

Writing

* Prefer surgical edits over rewrites.
* Do not refactor unrelated code.
* Preserve existing structure unless it blocks correctness.
* Maintain backward compatibility unless explicitly told otherwise.

⸻

3. Change Strategy

Default posture

* Smallest change that achieves correctness.
* No speculative improvements.
* No aesthetic-only edits.

When modifying code

* Keep function signatures stable unless required.
* Avoid cascading changes across modules.
* Contain side effects.

⸻

4. Validation Requirements

Before declaring completion:

* Code compiles or runs (if applicable)
* No obvious runtime errors
* Imports resolve
* Logic is internally consistent

If execution is not possible, perform a reasoned validation pass.

⸻

5. Output Contract

Responses must be:

* Concise
* Deterministic
* Free of filler or conversational framing

Include only:

* What changed
* Why it changed
* Any required follow-up

Do not include:

* Apologies
* Motivational language
* Redundant summaries

⸻

6. Session Management Heuristics

* If context becomes noisy or unrelated → recommend new session
* If interaction length increases → suggest /cost
* Do not carry stale assumptions forward

⸻

7. System Architecture Reference

Application Type

Hybrid system:

* Streamlit → UI layer
* Flask → backend + database

Entry point:

* app.py

⸻

Core Subsystems

UI Components (components/)

* Modular Streamlit blocks
* Each file = isolated UI unit
* No cross-component coupling unless required

⸻

Plugin System (utils/plugins/)

Dynamic tool architecture.

Contract:

* Subclass AgentTool
* Implement:
    * validate_inputs(inputs: Dict) -> bool
    * execute(inputs: Dict) -> Dict

Lifecycle:

1. Registry reset
2. discover_tools("plugins")
3. Dynamic import
4. Class registration

Do not break this pattern.

⸻

Database (utils/database.py)

Models:

* TrainingConfig
* TrainingMetric

Constraints:

* Must support PostgreSQL and SQLite
* Use SQLAlchemy abstractions only
* Respect migration flow (Flask-Migrate)

⸻

Training System (utils/)

* peft_trainer.py → LoRA / PEFT
* distributed_trainer.py → multi-GPU
* model_inference.py
* model_versioning.py
* visualization.py

Changes here must not break:

* training reproducibility
* parameter compatibility

⸻

8. Critical Flows

Plugin Loading

* Triggered at app startup
* Registry must be cleared before discovery
* Duplicate registration is a failure condition

⸻

Training Workflow

1. Dataset selection
2. Validation
3. Parameter configuration
4. Config validation
5. Persist config
6. Track via session state

Do not alter ordering without justification.

⸻

Database Initialization

* Retry (3 attempts, exponential backoff)
* Connection pooling enforced
* SQLite fallback required

Failure to preserve fallback = critical error

⸻

9. Environment Constraints

* DATABASE_URL → primary DB selector
* SPACE_ID → UI context modifier
* SQL_DEBUG → logging toggle

Code must not assume presence of any variable.

⸻

10. Code Standards

* PEP 8 compliant
* Max line length: 88
* Type hints required
* Structured logging only
* Use context managers for resource safety

⸻

11. CI/CD Awareness

* Lint must pass (Flake8 critical rules)
* Tests must not regress
* HF deployment depends on:
    * correct artifacts
    * HF_TOKEN

Do not introduce CI-breaking changes.

⸻

12. Failure Modes to Avoid

* Rewriting large files unnecessarily
* Breaking plugin discovery
* Introducing DB-specific logic (must stay portable)
* Silent changes to training behavior
* Cross-module ripple effects

⸻

13. Escalation Conditions

Pause and reassess if:

* Multiple architectural paths exist
* Change requires cross-system refactor
* Requirements are ambiguous

In these cases, ask for clarification (max 3 questions).

⸻

14. Definition of Done

A task is complete when:

* The requested change is implemented
* No regressions are introduced
* System invariants remain intact
* Output follows Section 5

⸻

15. Meta Constraint

Do not optimize for elegance.

Optimize for:

* correctness
* stability
* minimal surface area of change

⸻