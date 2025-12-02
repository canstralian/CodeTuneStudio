# GitHub Copilot and Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
- **Objective**: Establish a consistent Copilot and Codex setup that enforces strict code quality, security, and automation standards for all Trading Bot Swarm repositories.
- **Role of Copilot**: Operate as a disciplined pair programmer—suggest but never auto-commit, avoid speculative code, and always align with project conventions, security defaults, and testing requirements.
- **Audience**: Contributors, reviewers, and maintainers configuring AI-assisted workflows, CI/CD, and release automation across bots, shared libraries, and ops tooling.

## Configuration Overview
- **Testing**: Default to running the smallest scope first (unit ➜ integration ➜ e2e). Treat missing or flaky tests as blockers; require reproducible seeds for randomness.
- **Linting & Code Style**: Enforce project linters (e.g., `ruff`, `flake8`, `eslint`, `prettier`) with pre-commit hooks. Prefer explicit imports, typed interfaces, and small pure functions; avoid try/except around imports.
- **Async Patterns**: Favor asyncio-friendly libraries, never block the event loop, use timeouts/backpressure, and propagate cancellations. Wrap external I/O with circuit breakers and retries that use jittered backoff.
- **Security Defaults**: Disable unsafe eval/exec, disallow secrets in logs, and require parameterized queries and prepared statements. Mandate SBOM generation, dependency pinning, and SAST/DAST gates.
- **Logging & Observability**: Standardize structured logs (JSON), correlate request IDs/trace IDs, and export metrics/traces to the shared telemetry stack. Treat log level mismatches as review findings.
- **CI/CD Integration**: Require lint + test + security scans on every PR. Block merges on quality gates and fail fast with clear remediation steps. Cache dependencies but never cache secrets.
- **Version Control**: Use conventional commits, short-lived branches, and rebases over merges when possible. Protect `main` with required checks and signed tags.

## Custom Instruction Behavior for Copilot and Codex
- **General Rules**:
  - Follow repository-specific CONTRIBUTING standards before proposing code.
  - Prefer minimal, verifiable suggestions with references to existing utilities.
  - Never bypass tests or linters; remind authors to run the relevant suite for touched areas.
  - Ignore documentation-only changes when advising on required test execution.
- **Example Rules (Conceptual)**:
  - Reject prompts that request credential handling or weakening security controls.
  - Promote idempotent scripts and deterministic outputs.
  - Surface async-safety concerns (e.g., blocking calls, missing timeouts) in suggestions.
- **Sample Custom Instructions (YAML)**:
  ```yaml
  copilot:
    role: disciplined_pair_programmer
    enforce:
      - always reference project lint/test commands
      - suggest smallest safe change first
      - call out missing error handling, timeouts, and input validation
      - do not suggest committing or pushing code
      - skip test reminders for doc-only diffs
  codex:
    role: code_reviewer_plus_builder
    enforce:
      - respond with repo-specific style guides and security defaults
      - ensure async patterns are non-blocking and cancellable
      - require threat-aware logging (no secrets, structured JSON)
      - insist on running tests/linters for code changes
      - refuse unsafe operations (eval/exec, raw SQL)
  ```

## GitHub Workflow Example: Lint and Test Automation
- **Trigger Conditions**: `pull_request` and `push` to `main` and release branches; optional `workflow_dispatch` for manual reruns.
- **Quality Gate Job**:
  ```yaml
  name: Lint and Test
  on:
    pull_request:
      branches: [main, release/*]
    push:
      branches: [main, release/*]
    workflow_dispatch:
  permissions:
    contents: read
    checks: write
    pull-requests: write
  jobs:
    quality-gate:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.11'
            cache: pip
        - name: Install dependencies
          run: pip install -r requirements.txt
        - name: Lint
          run: |
            ruff check .
            mypy .
        - name: Tests
          run: pytest --maxfail=1 --disable-warnings -q
        - name: Upload coverage
          if: success()
          uses: codecov/codecov-action@v4
  ```

## Semantic Release, Version Tagging, and Automation
- **Best Practices**:
  - Enforce semantic versioning with conventional commits; release only from protected `main`.
  - Automate CHANGELOG generation and signed tags.
  - Use dry-run mode on PRs to validate release notes without publishing.
- **Example Semantic Release Workflow**:
  ```yaml
  name: Semantic Release
  on:
    push:
      branches: [main]
  permissions:
    contents: write
    packages: write
    id-token: write
  jobs:
    release:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with:
            node-version: '20'
        - run: npm ci
        - run: npx semantic-release
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

## Security and Dependency Scanning
- **Approach**: Run SCA and SAST on PRs and nightly schedules; fail builds on critical findings and create issues automatically.
- **Example Security Workflow**:
  ```yaml
  name: Security Scan
  on:
    pull_request:
      branches: [main, release/*]
    schedule:
      - cron: '0 2 * * *'
  permissions:
    security-events: write
    contents: read
    actions: read
  jobs:
    sast:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: CodeQL Init
          uses: github/codeql-action/init@v3
          with:
            languages: python, javascript
        - name: CodeQL Analyze
          uses: github/codeql-action/analyze@v3
    dependency-review:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Dependency Review
          uses: actions/dependency-review-action@v4
  ```

## Contributor Guidelines
- **Proposing Changes**: Open an issue with scope, risks, and testing plan. For PRs, include clear checklists for linting, tests, security scans, and doc impacts.
- **Review Criteria**: Consistency with guide rules, passing CI, threat modeling for new integrations, observability coverage, and rollback strategy.
- **Validation Process**: Require reviewer sign-off, green pipelines, and artifact verification (coverage reports, SBOMs, and release dry-runs when applicable).

## Troubleshooting and Optimization
- Re-run failed jobs with increased logging; use `--maxfail=1` for quick isolation.
- Cache restoration issues: clear cache keys when upgrading dependencies or toolchains.
- Flaky async tests: add timeouts and fake clocks; avoid real network calls.
- Coverage drops: prioritize high-risk paths (auth, trading logic, risk checks) before peripheral utilities.

## Maintenance Schedule
- **Quarterly**: Refresh tool versions, runner images, and linters; update default Python/Node versions.
- **Monthly**: Rotate tokens/secrets, validate SBOM generation, and audit workflow permissions.
- **Per Release**: Confirm semantic-release configs, bump pinned dependencies, and validate observability defaults.

## Closing Note
Standardizing excellence in Copilot and Codex workflows strengthens reliability, performance, and safety across the Trading Bot Swarm ecosystem. Use this guide as the canonical reference for AI-assisted development and automation.
