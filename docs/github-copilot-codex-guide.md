# Comprehensive GitHub Copilot and Codex Guide for Trading Bot Swarm

## Purpose and Scope
- Establish a single, authoritative playbook for configuring GitHub Copilot and Codex across the Trading Bot Swarm ecosystem.
- Treat Copilot as a disciplined pair programmer with strict behavioral rules: it can propose changes, but humans own acceptance, review, and deployment decisions.
- Apply these standards to application code, infra-as-code, data/ML pipelines, automation scripts, and operational runbooks. Documentation-only changes may skip test execution but must still follow review and linting rules.
- Promote consistency, code quality, and secure automation to protect trading reliability and safety.

## Configuration Overview
- **Testing**
  - Every code change must include unit/integration coverage; run fast suites locally before PRs and rely on CI for slow/e2e jobs.
  - Prefer deterministic, hermetic tests that avoid live network calls unless explicitly mocked or recorded.
  - Capture coverage to enforce thresholds; quarantine and fix flaky tests before merge.
- **Linting & Formatting**
  - Enforce repo linters/formatters (e.g., `ruff`, `flake8`, `eslint`, `prettier`, `black`, `isort`).
  - Do not merge with lint errors; suppressions require justification and issue links.
- **Code Style & Architecture**
  - Follow existing patterns (dependency inversion, clear orchestration vs. pure logic boundaries, explicit typing/return values).
  - Prefer small, composable functions and pure functions for pricing/signal logic.
  - Maintain backward compatibility for APIs and contracts; deprecate with clear migration notes.
- **Async & Concurrency**
  - Use `async`/`await` for I/O-bound work; avoid blocking calls inside async paths.
  - Centralize concurrency controls (semaphores, rate limiters) with timeouts and graceful cancellation.
- **Security Defaults**
  - Never hardcode secrets; use secret managers or environment variables with least privilege.
  - Validate inputs at boundaries, sanitize logs, and avoid leaking PII/keys.
  - Require signed commits, branch protection, Dependabot alerts, and enforcement of minimal dependency scopes.
- **Logging & Observability**
  - Emit structured logs with correlation/request IDs; keep `info` for state changes, `warn` for recoverable issues, and `error` for action-required events.
  - Track metrics for latency, error rates, fills/rejections, queue depth, and cache hit rates; export traces for critical flows (order routing, strategy evaluation).
- **CI/CD Integration**
  - Mandatory quality gates: lint, type-check, unit tests, and security scan before deploy.
  - Fail the pipeline on coverage regressions or secret exposure findings; require human approval for overrides.
- **Version Control Practices**
  - Use small, focused PRs with clear titles/descriptions; rebase on `main` to keep history linear.
  - Prefer Conventional Commits to unlock automated releases; tag releases with semantic versions and signed tags.

## Custom Instruction Behavior for Copilot and Codex
- **Principles**
  - Match repository patterns, security controls, logging standards, and testing expectations.
  - Prefer minimal, reviewable edits; avoid large refactors unless explicitly requested.
  - Always propose applicable tests/linters for code changes; note when documentation-only edits may skip runtime tests.
  - Explain assumptions, call out risks, and suggest feature-flag/rollback strategies for risky changes.
- **Example Prompt Rules**
  - Respond with concise, actionable code plus rationale.
  - Surface required secrets/configuration and how to load them securely.
  - Enforce async-safe patterns and structured logging.
  - Provide minimal repro steps when diagnosing failures.
- **Conceptual Custom Instructions (YAML)**
```yaml
copilot:
  role: "pair programmer with strict guardrails"
  behavior:
    - follow project style, typing, lint, security, and observability defaults
    - propose tests for any code change; allow skipping runtime tests for docs-only edits
    - prefer small diffs; avoid unrequested refactors
    - use async-safe patterns, structured logging, and explicit timeouts
    - highlight configuration/secrets requirements without exposing secrets
    - recommend running: ["lint", "type-check", "unit-test"] before merge
  prohibited:
    - hardcoded credentials or bypassing validation
    - disabling logging/metrics/alerts without approval
    - introducing network calls to unknown hosts

codex:
  role: "automation assistant for CI/CD and scripting"
  behavior:
    - generate workflows/scripts aligned with CI, security, and observability rules
    - keep automation idempotent, parameterized (env vars/inputs), and auditable
    - require lint + tests for code changes; skip runtime tests only for documentation changes
    - propose rollback and verification steps for deployments
  prohibited:
    - destructive operations without confirmation gates
    - unpinned actions/dependencies that weaken supply-chain integrity
```

## GitHub Workflow Example: Lint & Test Automation
- **Triggers:** `pull_request` (opened, synchronize, reopened), `push` to protected branches, and manual `workflow_dispatch`. Ignore pure documentation paths for runtime steps.
- **Quality Gate Job:**
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
    timeout-minutes: 25
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
        if: success()
        uses: codecov/codecov-action@v4
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
- Use Conventional Commits so semantic-release can compute versions, update changelog, and publish signed tags/releases automatically.
- Gate releases on passing quality checks and signed commits; publish artifacts (containers, wheels) with provenance metadata.

### Security and Dependency Scanning
```yaml
name: security-and-deps
on:
  schedule:
    - cron: "0 3 * * *"  # daily
  workflow_dispatch: {}
  pull_request:
    paths-ignore:
      - "**/*.md"

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency review
        uses: actions/dependency-review-action@v4
  codeql:
    uses: github/codeql-action/.github/workflows/codeql.yml@v3
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
- Add image scanning for published containers and SBOM generation where applicable.
- Fail builds on critical/high vulnerabilities without approved risk acceptance.

## Contributor Guidelines
- **Proposing Changes:** Open an issue or draft PR describing scope, risks, rollout/rollback plan, and testing strategy. Keep PRs small and focused.
- **Review Criteria:**
  - Alignment with architecture decisions, security defaults, and logging/observability practices.
  - Adequate tests and coverage; deterministic behavior and no flaky tests.
  - Clean lint/type checks; parameterized configs; no secret exposure.
  - Release notes and feature flags documented when behavior changes.
- **Validation Process:**
  - Run lint, type-check, and tests locally or via CI; attach evidence (logs, coverage) in the PR description.
  - For infra changes, include plan/apply diffs, blast-radius analysis, and rollback steps.
  - For data/ML changes, document datasets, metrics, and reproducibility steps.

## Troubleshooting & Optimization Tips
- **Copilot/Codex noisy or off-pattern:** Reduce prompt scope, include codebase examples, or anchor to known-good files; regenerate with stricter instructions.
- **Slow CI runs:** Enable dependency caching, split lint/test jobs, parallelize matrices (Python/Node versions, databases), and reuse build artifacts.
- **Flaky tests:** Add timeouts, seed randomness, use deterministic fixtures/mocks, and quarantine flaky tests until fixed.
- **Security false positives:** Document suppressions with justification and ticket links; prefer fixing underlying issues and upgrading scanners.
- **Observability gaps:** Ensure correlation IDs propagate through async/background work; add health checks and SLO dashboards.

## Maintenance Schedule
- Review and refresh this guide quarterly or after major platform/tooling changes (CI stack, language/runtime upgrades, security policies).
- Archive superseded instructions while keeping change history for auditability.
- Align updates with the Trading Bot Swarm release calendar to ensure compatibility across services and shared libraries.

## Closing Note
Standardizing these practices elevates reliability, performance, and safety for the trading ecosystem while enabling Copilot and Codex to contribute responsibly and efficiently.
