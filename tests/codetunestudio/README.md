# CodeTuneStudio Canonical Test PR

## Purpose

This pull request exists to **intentionally fail CI**.

It is not a bug fix.
It is not a feature addition.
It is a **doctrine test**.

The goal of this PR is to demonstrate how CodeTuneStudio behaves when reviewing code under controlled conditions, so contributors and future maintainers can clearly understand:
- What CodeTuneStudio will flag
- What CodeTuneStudio will refuse to touch
- How it explains both decisions
- Why it never changes code automatically

**If this PR ever passes CI without changes to CodeTuneStudio itself, something is wrong.**

---

## What CodeTuneStudio Is (in This Repo)

CodeTuneStudio acts as a **CI/CD gate**, not an auto-refactoring tool.

Its role is closer to a senior reviewer than an automated formatter:
- It analyzes code changes
- It explains risks and violations
- It suggests fixes as diffs
- It fails the build when standards are not met
- It refuses to refactor when context is insufficient

**It never edits files.**
**It never guesses intent.**
**It never optimizes at the cost of safety or clarity.**

Human judgment is always required for final changes.

---

## Structure of This Test

This PR includes two deliberately different files to exercise both core behaviors.

### 1. `violation_examples.py` — Clear, Fixable Violations

This file contains obvious and intentional problems, such as:
- Missing input validation
- Hardcoded filesystem paths
- Weak or unsafe error handling

**Expected behavior:**
- CodeTuneStudio flags each issue
- Explains why it matters (correctness, security, maintainability)
- Provides suggested diffs showing how to fix it
- Fails CI

This demonstrates CodeTuneStudio's ability to enforce standards without ambiguity.

---

### 2. `ambiguous_refactoring.py` — Insufficient Context

This file represents code that might benefit from refactoring, but lacks critical context:
- No clear contract or schema
- Unknown side effects
- Unclear invariants or intent

**Expected behavior:**
- CodeTuneStudio explicitly refuses to suggest changes
- Explains what information is missing
- Does not provide speculative diffs
- Fails CI, but as a refusal rather than a violation

This demonstrates restraint. **Refusal is a feature, not a failure.**

---

## Why Refusal Matters

A system that always has an answer is not intelligent—it's reckless.

CodeTuneStudio treats missing context as a hard stop, not an invitation to guess. This is how it avoids:
- Silent logic changes
- Broken assumptions
- "Looks cleaner but behaves differently" bugs

**If the agent cannot justify a change with high confidence, it must explain why and step aside.**

---

## Success Criteria for This PR

This PR is considered successful if:
- CI fails deterministically
- Violations are clearly explained
- Suggested diffs are readable and actionable
- Refusals are explicit and calm
- No files are modified automatically
- A human reviewer can easily understand what to do next

**A green build is not success here.**
**Clarity and trust are.**

---

## Long-Term Role of This PR

This pull request serves as the **canonical reference** for CodeTuneStudio behavior.

Any future changes to CodeTuneStudio should be validated against this PR to ensure:
- Standards have not drifted
- Refusal behavior remains intact
- The agent still behaves like a careful senior reviewer

Think of this as a **living regression test for philosophy**, not just code.

---

## Final Note

If you are reading this because CI failed: **good**.
That means the system is working as designed.

Read the output. Apply changes deliberately.
Nothing here is automatic—by intent.
