# GitHub Copilot and Codex Configuration Guide for Trading Bot Swarm

## Purpose and Scope
- Establish a single source of truth for configuring GitHub Copilot and Codex inside the Trading Bot Swarm ecosystem.
- Treat Copilot as a disciplined pair programmer: it may propose code, but humans remain accountable for acceptance, review, and deployment decisions.
- Ensure consistency, code quality, and secure automation across services, agents, and shared libraries.
- Apply these instructions to application code, infrastructure-as-code, data pipelines, and operational scripts. Documentation-only changes are exempt from automated test requirements but must still follow review rules.

## Configuration Overview
- **Testing:**
  - All code changes must include unit/integration tests. Fast tests must run locally before opening a PR; slow/e2e tests run in CI or via scheduled jobs.
  - Prefer deterministic, hermetic tests; avoid network access unless explicitly mocked or recorded.
- **Linting & Formatting:**
  - Enforce project linters (e.g., `ruff`, `flake8`, `eslint`, `prettier`, `black`, `isort`).
  - Do not merge PRs with linter errors; fix or suppress with justification.
- **Code Style:**
  - Follow existing patterns and architecture decisions (dependency inversion, clear boundaries between orchestration and pure logic).
  - Keep functions small and side-effect free when possible; prefer pure functions for pricing and signal logic.
  - Provide type hints where supported; default to explicit return types.
- **Async Patterns:**
  - Use `async`/`await` for I/O-bound operations; avoid blocking calls in async contexts.
  - Centralize concurrency controls (semaphores, rate-limiters) and ensure graceful cancellation and timeouts.
- **Security Defaults:**
  - Never hardcode secrets. Use vault/secret managers and environment variables with least privilege.
  - Validate inputs at service boundaries; sanitize logs to avoid leaking PII/keys.
  - Require signed commits and enforce branch protection; enable Dependabot alerts.
- **Logging & Observability:**
  - Emit structured logs with correlation/request IDs; use log levels consistently (`debug` noisy, `info` for state changes, `warn` for recoverable issues, `error` for action needed).
  - Capture metrics for latencies, error rates, fills/rejections, and queue backlogs; export traces for critical paths (order routing, strategy evaluation).
- **CI/CD Integration:**
  - Mandatory quality gates: lint, type-check, unit tests, security scan before deploy.
  - Block merges if quality gates fail or coverage drops below target thresholds.
- **Version Control Practices:**
  - Small, reviewed PRs with clear titles/descriptions. Rebase onto main before merge to keep history linear.
  - Use conventional commits for release automation; tag releases with semantic versions.

## Custom Instruction Behavior
- **Principles for Copilot/Codex responses:**
  - Suggest code that matches repository patterns and respects security, logging, and testing rules.
  - Prefer minimal, targeted edits; avoid sweeping refactors without intent.
  - Always propose tests and linters for code changes; skip for documentation-only edits.
  - Explain assumptions, highlight risks, and suggest rollback/feature-flag strategies for risky changes.

### Example Rules for Prompts
- Respond with concise, actionable code suggestions plus rationale.
- Include testing guidance for any new/changed behavior.
- Call out required secrets/config variables and how to load them securely.
- For async code, ensure non-blocking patterns and timeouts are present.
- For logging, use structured contexts and avoid logging secrets.
- Offer minimal repro steps when diagnosing failures.

### Custom Instructions (Conceptual YAML)
```yaml
copilot:
  role: "pair programmer with guardrails"
  behavior:
    - follow project code style, typing, lint, and security defaults
    - propose tests for code changes; note when docs-only changes allow skipping tests
    - prefer small, reviewable diffs; avoid unrequested refactors
    - use async-safe patterns and structured logging for services
    - highlight configuration/secrets requirements without exposing secrets
    - recommend running: ["lint", "type-check", "unit-test"] before PR merge
  prohibited:
    - suggesting hardcoded credentials or bypassing validation
    - generating code that disables logging/metrics/alerts without approval

codex:
  role: "automation assistant for scripted tasks"
  behavior:
    - generate scripts/workflows consistent with CI/CD, security, and observability rules
    - keep automation idempotent and parameterized (env vars, inputs)
    - suggest rollback and verification steps for deployments
    - skip test runs for documentation-only changes; otherwise, require lint+tests
  prohibited:
    - destructive operations without confirmation gates
    - network calls to unknown hosts in automated jobs
```

### Reminder on Tests and Linters
- For any code change, run all applicable linters and tests locally or in CI before requesting review.
- Documentation-only PRs may skip automated test execution but must still pass linting rules for docs (markdown lint, link checks if configured).

## GitHub Workflow: Lint & Test Automation
- **Triggers:** `pull_request` (opened, synchronized, reopened), `push` to protected branches, and manual `workflow_dispatch`.
- **Quality Gate Job (example):**
```yaml
name: lint-and-test

on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths-ignore:
      - "**/*.md"
  push:
    branches: [main, release/*]
  workflow_dispatch: {}

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
      - name: Type Check
        run: |
          mypy .
      - name: Unit Tests
        run: |
          pytest --maxfail=1 --disable-warnings -q
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: success()
```

## Best Practice Workflows
### Semantic Release & Version Tagging
```yaml
name: semantic-release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
- Use Conventional Commits; semantic-release computes the next version, updates changelog, and tags/releases automatically.

### Security and Dependency Scanning
```yaml
name: security-scan
on:
  schedule:
    - cron: "0 3 * * *"  # daily
  workflow_dispatch: {}
  pull_request:
    paths-ignore:
      - "**/*.md"

jobs:
  dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency review
        uses: actions/dependency-review-action@v4
  codeql:
    uses: github/codeql-action/.github/workflows/codeql.yml@v2
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@v0
        with:
          scan-type: fs
          ignore-unfixed: true
          severity: CRITICAL,HIGH
```

## Contributor Guidelines
- **Proposing Changes:** Open an issue or draft PR describing scope, risks, rollout/rollback plan, and testing strategy. Keep PRs small and focused.
- **Review Criteria:**
  - Code aligns with architecture decisions, security defaults, and logging/observability practices.
  - Adequate tests and coverage; deterministic behavior and no flaky tests.
  - Lint/type checks clean; secrets not exposed; configs are parameterized.
- **Validation Process:**
  - Run lint, type-check, and tests locally or in CI. Provide evidence (logs, coverage) in the PR description.
  - For infra changes, include plan/apply diffs and rollback steps.
  - For data/ML changes, document datasets, metrics, and reproducibility steps.

## Troubleshooting & Optimization Tips
- **Copilot/Codex noisy or off-pattern:** Regenerate with smaller context, include examples from the codebase, or pin to known-good files.
- **Slow CI runs:** Enable dependency caching, split lint/test jobs, and parallelize matrix builds (Python/Node versions, database backends).
- **Flaky tests:** Add timeouts, seed randomness, and prefer deterministic fixtures/mocks. Quarantine flaky tests and fix before merge.
- **Security false positives:** Document suppressions with justification and ticket links; prefer fixing the underlying issue.
- **Observability gaps:** Ensure correlation IDs propagate through async tasks and background workers; add health checks and SLO dashboards.

## Maintenance Schedule
- Review and update this guide quarterly or after major platform/tooling changes (CI stack, language versions, security policy updates).
- Archive superseded instructions but keep change history for auditability.
- Align with the Trading Bot Swarm release calendar to ensure compatibility.

## Closing Note
Standardizing these practices strengthens the reliability, performance, and safety of the trading ecosystem while enabling Copilot and Codex to assist responsibly and efficiently.
