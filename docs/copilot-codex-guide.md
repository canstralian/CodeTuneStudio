# GitHub Copilot and Codex Configuration Guide for the Trading Bot Swarm

## Purpose and Scope
- Standardize how GitHub Copilot and Codex are configured and used as pair programmers.
- Enforce consistent behavior, code quality, security, and automation across all Trading Bot Swarm services.
- Apply to all contributors, CI jobs, and automation pipelines interfacing with the codebase.

## Role of Copilot as Pair Programmer
- Copilot acts as a suggestion engine, not an autonomous committer.
- Follow strict behavioral rules: no secret exfiltration, prefer existing patterns, avoid generating credentials, and suggest changes in the smallest reviewable increments.
- Suggestions must respect repository conventions (lint, formatting, typing, async patterns) and never bypass security controls.

## Configuration Overview
- **Testing**: Default to running unit and integration tests relevant to touched modules; favor `pytest -m "not e2e"` for fast validation and full suites in CI.
- **Linting/Formatting**: Enforce `ruff`/`flake8`, `black`, and `isort`/`ruff format` as configured. Reject suggestions that ignore lint rules.
- **Code Style**: Honor type hints, short functions, explicit returns, and clear docstrings. Prefer dependency injection and minimize global state.
- **Async Patterns**: Use `asyncio`/`trio` friendly code; avoid blocking calls in async contexts; wrap network I/O with timeouts and retries.
- **Security Defaults**: Require parameterized queries, secret management via environment/secret stores, input validation, CSRF protection in web surfaces, and least-privilege IAM. Deny suggestions that introduce plaintext secrets or weaken authz/authn.
- **Logging & Observability**: Standardize on structured logging with request IDs/trace IDs, emit metrics for critical paths, and propagate OpenTelemetry context when available.
- **CI/CD Integration**: Ensure generated changes include test/lint hooks, reusable workflows, and status checks. Prefer idempotent scripts.
- **Version Control**: Encourage small, atomic commits with descriptive messages, signed tags for releases, and conventional commit prefixes when possible.

## Custom Instruction Behavior (Copilot & Codex)
- Enforce running tests/linters for code changes; documentation-only changes may skip.
- Require reviewable diffs with comments explaining risky changes.
- Prefer existing utility functions before introducing new dependencies.

### Example Behavioral Rules
- Reject code that accesses network outside allowed endpoints.
- Require feature flags for experimental paths.
- Prefer configuration via environment variables and `.env` templates.
- Do not propose direct database migrations without validations and backups.

### Conceptual YAML for Custom Instructions
```yaml
copilot:
  role: pair-programmer
  required_behaviors:
    - respect_existing_patterns: true
    - run_tests_before_commit: true
    - run_linters_before_commit: true
    - skip_checks_for_docs_only: true
    - prefer_existing_utils: true
    - no_plaintext_secrets: true
    - enforce_timeouts_for_io: true
  review_prompts:
    - "Have you run pytest and lint for code changes?"
    - "Did you reuse an existing helper instead of adding a new dependency?"
    - "Are you avoiding blocking calls in async contexts?"
  prohibited:
    - generating_credentials
    - disabling_security_controls
    - committing_without_review

codex:
  role: automation_guardrail
  checks:
    - verify_tests_executed: true
    - verify_linters_executed: true
    - ensure_docs_only_changes_skip_checks: true
    - require_changelog_or_release_notes_for_features: true
  output_expectations:
    - short_diff_summaries
    - inline_security_callouts
```

## GitHub Workflow Example: Lint and Test Automation
Trigger on pull requests, pushes to `main`, and schedule for nightly assurance.

```yaml
name: quality-gate
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]
  schedule:
    - cron: "0 3 * * *"  # nightly

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          black --check .
      - name: Tests
        run: |
          pytest -m "not e2e" --maxfail=1 --disable-warnings -q
      - name: Upload coverage
        if: success()
        uses: codecov/codecov-action@v4
```

## Best-Practice Workflows

### Semantic Release and Version Tagging
```yaml
name: semantic-release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npx semantic-release
```
- Require conventional commits for automatic changelog and tag generation.
- Protect `main` with required checks before tags are created.

### Security and Dependency Scanning
```yaml
name: security-scan
on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1"  # weekly

jobs:
  deps-and-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Dependency review
        uses: actions/dependency-review-action@v4
      - name: Vulnerability scan
        uses: github/codeql-action/init@v3
        with:
          languages: python
      - name: CodeQL analyze
        uses: github/codeql-action/analyze@v3
      - name: Pip audit
        run: pip install pip-audit && pip-audit
```

## Contributor Guidelines
- Propose changes via draft PRs with linked issues and clear scope statements.
- Must include: tests, lint compliance, security impact notes, and rollback plan for risky changes.
- Review criteria: correctness, performance impact, observability, security posture, and alignment with style guides.
- Validation process: pre-commit hooks, CI quality gate, manual code review, and release checklist with sign-off.

## Troubleshooting and Optimization Tips
- **Copilot noise**: tighten context by selecting relevant files and add inline TODOs for focus.
- **Async timeouts**: set defaults (e.g., 5s) and expose overrides via config.
- **Flaky tests**: isolate external dependencies, add retries/backoff, and tag as `@flaky` until fixed.
- **Dependency conflicts**: prefer `pip-compile` with explicit Python version pins and hash-locked artifacts.
- **Performance hotspots**: add profiling hooks (`cProfile`, `py-spy`), cache heavy computations, and instrument metrics.

## Maintenance Schedule
- Quarterly review of Copilot/Codex instruction set and workflow YAMLs to reflect new stack defaults.
- Post-incident updates within 48 hours to capture new guardrails or fixes.
- Align guide revisions with major release milestones and dependency baseline updates.

## Closing Note
Standardizing these practices strengthens reliability, performance, and safety across the Trading Bot Swarm, ensuring every contribution upholds excellence.
