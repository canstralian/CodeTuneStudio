# GitHub Copilot + Codex Configuration Guide for Trading Bot Swarm

## Purpose and Scope
- Establish a standard for using GitHub Copilot and Codex as pair programmers that propose code but never bypass required checks.
- Align AI assistance with Trading Bot Swarm goals: reliability, performance, and safety in trading automation.
- Ensure consistent defaults for testing, linting, security, observability, and CI/CD so generated code always meets the same bar.

## Copilot and Codex Roles
- **Pair programmer only:** AI may suggest diffs, but humans own commits, reviews, and releases.
- **Security-first defaults:** Prefer least-privilege APIs, sanitized inputs, and secret-less local configs (use env vars/secret managers).
- **Guardrails:** Reject suggestions that add hardcoded secrets, weaken validation, skip logging/metrics in critical paths, or remove tests.
- **Async discipline:** Prefer async IO for network/DB calls; keep CPU-bound work in workers; avoid blocking event loops.
- **Reproducibility:** Preserve deterministic seeds, pinned dependencies, and idempotent migrations.

## Configuration Overview
- **Testing:**
  - Run unit tests on every PR; integration/e2e on main/nightly.
  - Enforce coverage thresholds for core trading logic and risk controls.
  - Provide fixtures for market data simulators; avoid real-exchange calls in CI.
- **Linting & Code Style:**
  - Use `ruff`/`flake8` + `black` for Python; `eslint` + `prettier` for JS/TS.
  - Disallow wildcard imports and unused symbols; keep functions < 50 LOC when practical.
- **Async Patterns:**
  - Use `asyncio` with `async/await`; wrap blocking calls in executors.
  - Timeouts on network calls; retries with jitter; circuit breakers around exchange gateways.
- **Security Defaults:**
  - No secrets in code; rotate tokens; validate all external payloads (JSON schema or pydantic).
  - Principle of least privilege for API keys; use role-scoped credentials for automation.
- **Logging & Observability:**
  - Structured logging (JSON) with trace/span IDs; log key trading decisions and risk checks.
  - Metrics: latency, error rate, fill ratio, PnL drift; alerts for risk breaches.
- **CI/CD Integration:**
  - Pre-commit hooks for format/lint; CI quality gate (lint + test + security scan).
  - Require green checks before merge; protected main with required reviews.
- **Version Control:**
  - Conventional commits; branch naming `feature/`, `fix/`, `chore/`, `exp/`.
  - Keep PRs small and focused; include test plan and rollback notes.

## Custom Instruction Behavior (Copilot & Codex)
- **Interaction Rules:**
  - Suggest minimal, safe diffs with comments explaining rationale.
  - Prefer standard libs before new dependencies; if needed, justify and pin versions.
  - When changing logic, propose matching tests. Skip doc-only changes in test gating.
- **Validation Defaults:**
  - Run linters and tests for code changes; doc-only changes may skip tests but must state "docs-only" in PR body.
  - Highlight potential race conditions, precision issues, and latency impact in trading paths.

### Example Custom Instructions (Conceptual YAML)
```yaml
ai_assist:
  role: "pair_programmer"
  principles:
    - "Never commit secrets or credentials"
    - "Prefer deterministic, testable code"
    - "Surface risks: latency, race conditions, precision"
  coding_guides:
    testing: "Add/extend unit tests for logic changes; run pytest"
    lint: "Run ruff/flake8 + black; no unused imports"
    async: "Use async IO; wrap blocking calls in executor; set timeouts"
    security: "Validate inputs; avoid eval/exec; use typed schemas"
    logging: "Structured JSON logs with correlation IDs"
  workflow:
    - "If only docs changed: note 'docs-only', skip tests"
    - "Else: run lint and tests before PR"
```

## GitHub Workflow: Lint & Test Automation
**Trigger:** `pull_request` on feature/fix branches; `push` to `main` for full suite.

```yaml
name: quality-gate
on:
  pull_request:
    branches: ["main", "develop"]
    paths-ignore:
      - "**/*.md"
      - "docs/**"
  push:
    branches: ["main"]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          black --check .
      - name: Tests
        run: pytest --maxfail=1 --disable-warnings --cov
```

## Best Practices: Release & Security Automation

### Semantic Release and Version Tagging
```yaml
name: semantic-release
on:
  push:
    branches: ["main"]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Security & Dependency Scanning
```yaml
name: security-scan
on:
  schedule:
    - cron: "0 6 * * *"
  pull_request:
    branches: ["main", "develop"]

jobs:
  sast-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency audit (pip)
        run: pip install pip-audit && pip-audit
      - name: CodeQL Init
        uses: github/codeql-action/init@v3
        with:
          languages: python, javascript
      - name: CodeQL Analyze
        uses: github/codeql-action/analyze@v3
```

## Contributor Guidelines
- Open an issue describing the change, risks, and rollout/rollback plan.
- For code changes: include tests, benchmark notes (if performance-sensitive), and security impact.
- Require at least one reviewer with domain knowledge; block merges on failing checks.
- Validation checklist: lint passes, tests green, threat model unchanged or improved, logs/metrics updated.

## Troubleshooting & Optimization
- **Copilot noise:** Reduce scope with inline comments; disable in secrets or credentials files.
- **Flaky tests:** Use deterministic seeds and isolated fixtures; quarantine and fix before merge.
- **Slow CI:** Enable caching (`pip cache`, `actions/cache`), shard tests, and parallelize lint/test.
- **False positives in scanners:** Suppress with documented allowlists and expiration dates.

## Maintenance Schedule
- Review this guide quarterly or with major dependency/CI changes.
- After each incident or postmortem, update guardrails, test cases, and release rules.

## Closing Note
Standardizing excellence keeps Trading Bot Swarm reliable, performant, and safe—Copilot and Codex assist, but engineering rigor leads the way.
