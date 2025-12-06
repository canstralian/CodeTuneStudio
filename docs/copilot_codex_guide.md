# Trading Bot Swarm: Copilot & Codex Configuration Guide

## Purpose and Scope
- Standardize how GitHub Copilot and Codex operate as disciplined pair-programmers across Trading Bot Swarm.
- Enforce consistent code quality, security, observability, and delivery practices.
- Provide actionable automation patterns (lint, test, release, scanning) tuned for code, infra-as-code, data, and async workflows.
- Clarify contributor expectations, review gates, and maintenance cadence for this guide.

## Role of Copilot and Codex
- Copilot: interactive pair-programmer that **never self-merges**, **never bypasses reviews**, and **always follows project rules** before suggesting code.
- Codex: structured generator for schemas, pipelines, and transformations; treated as a deterministic adapter that must satisfy validations/tests for each layer of the system.
- Both must:
  - Prefer least-privilege patterns and secure defaults (e.g., prepared statements, secret managers, no plaintext secrets).
  - Align with repo style (formatters, linters, typing rules, logging contracts, and async guidelines).
  - Surface rationales in suggestions (why this pattern, how it meets constraints).
  - Avoid generating TODOs; propose complete, testable units.

## Configuration Overview
- **Testing:** Mandatory for code changes; unit/integration tests co-located; fast tests on PRs, heavier suites on main/nightly. Skippable only for doc-only changes.
- **Linting & Formatting:** Enforce `ruff`/`flake8` + `black` (Python), `eslint`/`prettier` (JS/TS), `sqlfluff` (SQL) where applicable.
- **Code Style:** Typed Python (`mypy`/`pyright`), explicit interfaces, stable public APIs, clear docstrings. Avoid global state; prefer dependency injection.
- **Async Patterns:** Use `asyncio` with timeouts, cancellation handling, and backpressure; never block event loops; instrument tasks with structured logs and traces.
- **Security Defaults:** Secrets via vault/CI secrets; parameterized queries; input validation with Pydantic; principle of least privilege; avoid wild-card IAM.
- **Logging & Observability:** Use structured logging (JSON fields), correlation IDs, OpenTelemetry traces/metrics; log levels consistent (`info` baseline, `warning` for recoverable anomalies, `error` for failures).
- **CI/CD Integration:** PR quality gates (lint, test, type-check), artifact caching, coverage thresholds, signed releases, protected main branch.
- **Version Control:** Conventional commits; feature branches; rebase over merge commits for PR prep; semantic-release for automated tags.

## Custom Instruction Behavior (Conceptual)
Use these rules as the baseline policy surfaced to Copilot/Codex via editor/CLI settings.

### Example Rules
- Always run formatters/linters/tests before proposing completion for code changes.
- Reject suggestions that introduce secrets, disable security controls, or skip tests.
- Prefer idempotent, deterministic functions with explicit inputs/outputs.
- Provide brief inline rationale comments only when non-obvious; avoid noise.
- When touching async code, ensure timeouts and cancellation paths exist.

### Custom Instructions (YAML Concept)
```yaml
pair_programmer:
  role: "Guard-railed assistant for Trading Bot Swarm"
  always_require:
    - run: ["lint", "test", "typecheck"]
    - enforce_security: true
    - follow_codeowners: true
    - obey_branch_protection: true
  deny:
    - secrets_in_code: true
    - skipping_tests: true
    - unchecked_network_calls: true
  coding_guides:
    python:
      formatters: ["black"]
      linters: ["ruff"]
      typing: "mypy"
    javascript:
      formatters: ["prettier"]
      linters: ["eslint"]
    async:
      timeout_ms: 5000
      cancellation_required: true
      instrument: "otel"
  docs_only_changes:
    skip_checks: ["lint", "test"]
    note: "Only when no code/config touched"
```

## GitHub Workflow: Lint & Test Automation
Trigger on pull requests to `main` and `release/*`, and on pushes to `main`.

```yaml
name: quality-gate
on:
  pull_request:
    branches: [main, "release/*"]
    paths-ignore: ["**/*.md", "docs/**"]
  push:
    branches: [main]
    paths-ignore: ["**/*.md", "docs/**"]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          black --check .
      - name: Type check
        run: mypy .
      - name: Test
        run: pytest --cov=. --cov-report=xml:coverage.xml --maxfail=1 --disable-warnings -q
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
```

## Semantic Release & Version Tagging
- Adopt `semantic-release` for automated versioning and changelog generation based on conventional commits.
- Protect main; releases originate from main after passing quality gate.
- Example workflow:

```yaml
name: release
on:
  push:
    branches: [main]

jobs:
  semantic-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install semantic-release
        run: npm install --no-save semantic-release @semantic-release/{git,github,changelog}
      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

## Security & Dependency Scanning
- Integrate scanning into CI to block vulnerable changes.

```yaml
name: security-scan
on:
  pull_request:
    branches: [main, "release/*"]
  schedule:
    - cron: "0 6 * * *"  # daily

jobs:
  codeql:
    uses: github/codeql-action/codeql-analysis.yml@v3

  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Python dependency scan
        uses: pypa/gh-action-pip-audit@v1
      - name: Node audit (optional)
        run: npm audit --audit-level=high || true  # fail on high/critical in gating job
```

## Contributor Guidelines
- Open an issue or discussion for significant changes; align with design/architecture documents.
- Use feature branches; keep PRs focused and small.
- Follow conventional commit messages; include tests and updated configs.
- PR checklist: lint, type-check, tests, security scan results, coverage note, rationale for design choices.
- Review criteria: code clarity, adherence to async/security/logging standards, test completeness, observability hooks, rollback safety.
- Validation: reviewers verify CI results, rerun targeted tests if needed, confirm no secrets or unstable APIs.

## Troubleshooting & Optimization
- **Flaky tests:** add retries with backoff, isolate state, ensure deterministic seeds.
- **Slow pipelines:** enable dependency caching, parallelize test shards, prune coverage collection to changed paths.
- **Lint noise:** align local configs with CI; pin tool versions.
- **Type errors in async code:** confirm awaited tasks, explicit types for coroutines, and cancel tokens on shutdown.
- **Security false positives:** suppress only with linked issue and narrow scope.

## Maintenance Schedule
- Quarterly review of this guide alongside CI configs and CODEOWNERS.
- Immediate updates after new security requirements or tooling changes.
- Versioned changelog entry for each revision; communicate via release notes.

## Closing Note
By standardizing Copilot and Codex behavior, quality gates, and automation patterns, we reinforce reliability, performance, and safety across the Trading Bot Swarm ecosystem.
