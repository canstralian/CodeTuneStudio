# GitHub Copilot and Codex Configuration Guide for the Trading Bot Swarm

## Purpose and Scope
- Define how GitHub Copilot and Codex operate as disciplined pair programmers that never bypass testing, linting, or security expectations.
- Standardize contributor experience across bots, services, plugins, and automation scripts so code quality and safety remain consistent.
- Serve as the single reference for observability, CI/CD, and release automation expectations within the Trading Bot Swarm ecosystem.

## Configuration Overview
### Copilot as a Pair Programmer
- Treat Copilot suggestions as drafts that must be validated by humans and project automation before merge.
- Prompt Copilot with desired behavior, test expectations, and security constraints; reject suggestions lacking these elements.
- Do not allow Copilot to create documentation-only pull requests unless explicitly requested by the author.

### Testing and Linting
- Run unit, integration, and smoke tests for any executable change (`pytest` for Python, `jest`/`vitest` for JS/TS, `tox` or `uv run` for multi-env).
- Execute linters and type checkers before requesting review: `ruff`/`flake8`, `eslint`/`prettier`, `mypy`/`pyright`/`tsc`, and `shellcheck` for Bash utilities.
- Treat lint or test failures as blockers; rerun after addressing findings. Skip automation only for documentation-only changes.

### Code Style and Async Patterns
- Follow repository formatting defaults (Black-compatible width, import sorting via `ruff`, Prettier for web assets).
- Prefer dependency injection, explicit typing, and small, composable functions.
- In async paths, avoid blocking calls; use timeouts, cancellation tokens, and retry/backoff helpers provided by the platform utilities.

### Security Defaults
- Apply least-privilege access; never hard-code secrets or tokens.
- Enforce parameterized queries, validated inputs, and sanitized logging to prevent leakage of credentials or PII.
- Require CVE review and security release notes for dependency upgrades; favor signed commits and verified tags.

### Logging and Observability
- Use the shared logging utilities for structured JSON logs that carry correlation/trace IDs.
- Emit metrics (Prometheus/OpenTelemetry) for latency, order volume, error rates, and queue depths; attach alerts to SLOs.
- Capture audit events for configuration changes, model updates, and privileged actions.

### CI/CD Integration
- Protect `main` with required checks (lint, tests, security scans) and mandatory reviews.
- Use staged rollouts with canary or shadow deployments; enable automatic rollback on failing health checks.
- Keep infrastructure-as-code and environment configs versioned; Copilot suggestions must respect environment-specific settings.

### Version Control Workflow
- Use short-lived branches prefixed by intent (`feat/`, `fix/`, `chore/`, `sec/`); prefer rebase over merge commits.
- Adopt Conventional Commits to keep history and semantic release signals clear.
- Require green quality gates before squash-merging to `main` and before tagging releases.

## Custom Instruction Behavior for Copilot and Codex
### Behavioral Principles
- Suggest only code that compiles, passes linters, and honors security controls; highlight missing tests.
- Never auto-commit or bypass human review; flag when secrets or environment variables are required.
- Ignore documentation-only edits for automation triggers unless explicitly requested.

### Example Rules
1. Respect domain boundaries (`core/`, `plugins/`, `components/`, `utils/`); reuse existing abstractions first.
2. Annotate public functions with type hints and docstrings; prefer explicit imports.
3. Mirror feature changes with matching tests in `tests/` using the same module path.
4. Apply structured logging and correlation IDs in new async flows.

### Conceptual YAML Custom Instructions
```yaml
copilot:
  role: "Pair programmer with strict compliance focus"
  must_do:
    - "Surface required tests and linters for every code change"
    - "Decline documentation-only updates unless explicitly requested"
    - "Call out security, secrets, and data-handling requirements"
    - "Reference existing modules before generating new helpers"
  must_not_do:
    - "Bypass human review or commit directly"
    - "Generate secrets, tokens, or placeholder credentials"
    - "Offer blocking calls inside async workflows"
  defaults:
    testing: ["pytest", "integration", "smoke"]
    linting: ["ruff", "flake8", "eslint", "prettier"]
    typing: ["mypy", "pyright", "tsc"]
    security: ["secret-scanning", "least-privilege", "parameterized-queries"]

codex:
  role: "Automation-focused reviewer and enforcer"
  behaviors:
    validation:
      - name: "Tests"
        commands: ["pytest", "uv run pytest"]
      - name: "Lint"
        commands: ["ruff check .", "eslint ."]
      - name: "Types"
        commands: ["mypy", "tsc"]
    ignore_paths:
      - "docs/**"
      - "*.md"
  approvals:
    required_checks: ["lint", "test", "security-scan"]
```

## GitHub Workflow Example: Lint and Test Automation
Trigger on pull requests and pushes to `main` that touch code (ignore `docs/**` and `*.md`).
```yaml
name: lint-and-test
on:
  pull_request:
    paths-ignore: ["docs/**", "**/*.md"]
  push:
    branches: ["main"]
    paths-ignore: ["docs/**", "**/*.md"]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: ruff check .
      - name: Type check
        run: mypy .
      - name: Test
        run: pytest --maxfail=1 --disable-warnings -q
      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: ./.coverage*
```

## Best-Practice Workflows
### Semantic Release and Version Tagging
```yaml
name: release
on:
  push:
    branches: ["main"]

jobs:
  semantic-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install
        run: npm ci
      - name: Lint & Test
        run: npm run lint && npm test
      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

### Security and Dependency Scanning
```yaml
name: security-scan
on:
  schedule:
    - cron: "0 3 * * *"
  pull_request:
    paths-ignore: ["docs/**", "**/*.md"]

jobs:
  dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency audit
        run: pip install pip-audit && pip-audit

  codeql:
    uses: github/codeql-action/analyze@v3
    permissions:
      actions: read
      contents: read
      security-events: write
```

## Contributor Guidelines
- Propose changes through draft pull requests with linked issues and concise scope statements.
- Include tests, type checks, and lint fixes with the code changes; document only when behavior changes.
- Reviewers validate: test coverage, security posture (secrets, input validation), observability hooks, and adherence to async and style conventions.
- Use checklists for validation: tests green, linters clean, security scans passed, logging/metrics added where applicable, and release notes updated when needed.

## Troubleshooting and Optimization
- If Copilot suggestions are low-quality, provide more context (file paths, expected tests, security constraints) or reduce prompt scope.
- For flaky tests, mark and triage with retry/backoff, then stabilize before merge; avoid ignoring failures.
- Resolve lint noise by aligning local tool versions with CI; prefer `uv` or `pip-tools` for reproducible installs.
- When CI queues are long, run targeted jobs locally (`ruff`, `pytest -k <pattern>`) before pushing to reduce cycles.

## Maintenance Schedule
- Review this guide monthly or whenever CI policies, security baselines, or dependency tooling change.
- Align updates with major release milestones to keep semantic-release rules, scanner configurations, and branch policies current.
- Archive superseded workflows and record deltas in release notes for traceability.

## Closing Note
Standardizing excellence across Copilot and Codex usage strengthens the reliability, performance, and safety of the Trading Bot Swarm ecosystem. Treat these guidelines as the contract for high-quality, secure automation.
