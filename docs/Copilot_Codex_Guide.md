# Trading Bot Swarm – GitHub Copilot & Codex Configuration Guide

## Purpose and Scope
This guide standardizes how GitHub Copilot and Codex operate inside the Trading Bot Swarm ecosystem. It defines behavior expectations, coding guardrails, and automation practices so AI pair programmers reinforce reliability, performance, and safety rather than bypassing them.

## Configuration Overview
- **Pair-programming role:** Copilot/Codex act as proactive reviewers—suggestions must follow project rules before acceptance.
- **Testing:** Always add or update automated tests for functional changes. Skipping tests requires documented justification in PRs.
- **Linting & formatting:** Enforce `ruff` (Python) and `eslint`/`prettier` (JS/TS) where applicable. Fail CI on lint errors. Auto-format before commit.
- **Code style:** Prefer type hints, small pure functions, dependency injection, and minimal shared state. Avoid magic numbers; keep configuration in `settings`/env vars.
- **Async patterns:** Use `asyncio`-safe primitives, propagate cancellations, and avoid blocking calls in async paths. Prefer timeouts for network/IO calls.
- **Security defaults:** Deny-by-default for network and file access, validate inputs, escape outputs, and use parameterized queries. Secrets stay in vault/CI secrets, never in repo or logs.
- **Logging & observability:** Use structured logging with correlation IDs. Emit metrics for latency, throughput, and error rates. Prefer OpenTelemetry-compatible exporters.
- **CI/CD integration:** Every PR runs lint + tests + security scans. Require green CI before merge. Release pipelines gate on quality and changelog generation.
- **Version control:** Small, incremental PRs with clear scope; rebase on latest `main` before opening. Conventional Commits for history clarity.

## Custom Instruction Behavior
### Example Rules for Copilot and Codex
- Follow repository coding standards and security checklist before proposing code.
- Always surface missing tests or lint steps in suggestions.
- Avoid generating credentials, tokens, or sample secrets.
- Prefer explicit error handling and actionable log messages.
- Flag long-running tasks lacking timeouts or retries.
- Respect dependency constraints and prefer stable versions over latest when uncertain.

### Conceptual YAML for Custom Instructions
```yaml
copilot:
  role: "strict pair programmer"
  priorities:
    - enforce_security
    - suggest_tests
    - adhere_style_guides
  rules:
    - "Never propose secrets or unsafe shortcuts"
    - "Highlight missing type hints and logging context"
    - "Prefer idempotent, retry-safe patterns"
  ignore:
    - "Documentation-only changes do not require new tests"

codex:
  role: "code reviewer and generator"
  priorities:
    - catch_regressions
    - improve_performance
    - maintain_observability
  rules:
    - "Require lint/test execution for code changes"
    - "Call out concurrency hazards and blocking IO"
    - "Suggest dependency pins compatible with supported Python versions"
  ignore:
    - "Whitespace-only diffs"
```

## Workflow Example: Lint and Test Automation
Trigger on pull requests and pushes to main branches to enforce the quality gate.
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          pylint core plugins utils || true  # tighten to required once clean
      - name: Tests
        run: |
          pytest --maxfail=1 --disable-warnings -q
```

## Semantic Release & Version Tagging
- Use semantic versioning and Conventional Commits (`feat:`, `fix:`, `chore:`).
- Automate release notes and tags via `semantic-release` after CI success on `main`.
```yaml
name: Release
on:
  push:
    branches: [main]
jobs:
  semantic-release:
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

## Security and Dependency Scanning
- Run `pip-audit`/`npm audit` and SAST (e.g., `gitleaks`, `bandit`) on PRs.
- Enable Dependabot for automated updates.
```yaml
name: Security
on:
  schedule:
    - cron: "0 3 * * *"
  pull_request:
    paths:
      - "**/*.py"
      - "**/package*.json"

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Python security
        run: |
          python -m pip install --upgrade pip
          pip install pip-audit bandit
          pip-audit
          bandit -r .
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: JavaScript security
        run: |
          npm install --package-lock-only
          npm audit --audit-level=high || true
```

## Contributor Guidelines
- **Proposals:** Open an issue describing intent, risk, and rollback plan. Link to relevant trading strategies/components.
- **Review criteria:** Security posture, test coverage, performance impact, observability hooks, and alignment with style guides.
- **Validation:** PRs must show lint and test runs; deployment changes require staging verification notes.

## Troubleshooting & Optimization
- **Copilot noise:** Narrow context with file-specific instructions or reduce suggestion span.
- **Dependency conflicts:** Regenerate lockfiles per supported Python matrix (`3.9`–`3.11`), prefer compatible pins over latest.
- **Flaky tests:** Add timeouts, deterministic seeds, and isolate network dependencies with mocks.
- **Performance hotspots:** Profile async flows, batch network calls, and use circuit breakers for downstream services.

## Maintenance Schedule
- Quarterly review of tooling versions, supported Python/Node runtimes, and CI job durations.
- Monthly scan of security tooling rules and dependency update cadence.
- After major trading feature launches, refresh custom instructions to reflect new invariants.

## Closing Note
Standardizing Copilot and Codex behavior raises the reliability, performance, and safety of the Trading Bot Swarm. Apply these rules consistently to keep automation aligned with our engineering bar.
