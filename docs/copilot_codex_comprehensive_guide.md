# Comprehensive GitHub Copilot & Codex Guide for Trading Bot Swarm

## Purpose and Scope
- Define how GitHub Copilot and Codex act as disciplined pair programmers that propose code but never bypass required human review, quality gates, or security controls.
- Standardize testing, linting, code style, async discipline, security defaults, logging/observability, CI/CD integration, and version control so AI-assisted changes remain reliable and auditable.
- Apply to all Trading Bot Swarm services, libraries, automation scripts, and operational tooling; documentation-only updates remain reviewable but may skip automated tests when explicitly noted.

## Configuration Overview
- **Testing**
  - Require unit tests for all logic changes; add integration/e2e tests for trading flows, exchange adapters, and risk controls.
  - Use deterministic fixtures and seeded randomness; avoid live exchange calls in CI (mock or record instead).
  - Enforce coverage thresholds on core pricing, execution, and risk modules; fail PRs that reduce coverage without justification.
- **Linting & Code Style**
  - Python: `ruff`/`flake8` + `black`; JS/TS: `eslint` + `prettier`; infra-as-code uses the repo’s linters (e.g., `tflint`, `ansible-lint`).
  - Prefer explicit imports, typed signatures, and functions under ~50 LOC where practical; keep public APIs stable and documented.
  - Never add try/except wrappers around imports; fix root causes instead.
- **Async Patterns**
  - Use `async/await` for I/O; wrap blocking CPU or I/O in executors; set timeouts and cancellation paths for network/DB calls.
  - Centralize retries with jitter and circuit breakers around exchange/broker gateways.
- **Security Defaults**
  - No hardcoded secrets; load via env vars/secret managers; enforce least privilege and scoped tokens.
  - Validate all external payloads (pydantic/JSON schema); sanitize logs; prefer signed commits and protected branches.
- **Logging & Observability**
  - Structured JSON logging with correlation/trace IDs; log risk decisions, order intents, and error contexts without leaking secrets.
  - Emit metrics for latency, error rates, fill ratios, and PnL drift; surface alerts for SLA/SLO breaches.
- **CI/CD Integration**
  - Pre-commit hooks for format + lint; CI quality gates for lint, type checks, tests, and security scans before merge.
  - Use preview environments/feature flags for risky changes; require rollback notes in PRs.
- **Version Control Practices**
  - Conventional commits; branch naming `feature/`, `fix/`, `chore/`, `exp/`.
  - Keep PRs small, focused, and rebased; include test evidence and release/rollback considerations.

## Custom Instruction Behavior for Copilot & Codex
- **Behavioral Rules**
  - Act as pair programmers: propose minimal, context-aware diffs; humans own commits and releases.
  - Always mention required tests/linters for code changes; explicitly state when docs-only edits allow skipping tests.
  - Prefer existing dependencies/patterns; justify and pin versions when new packages are necessary.
  - Flag risks (latency, race conditions, precision, security) and suggest mitigations/feature flags.
- **Example Rules (Conceptual YAML)**
```yaml
ai_assist:
  role: "pair_programmer_with_guardrails"
  principles:
    - never commit secrets or weaken validation/logging
    - prefer deterministic, test-backed code with typed interfaces
    - highlight risk, latency, and precision impacts
  defaults:
    testing: ["pytest", "integration when logic changes"]
    linting: ["ruff", "black --check"]
    typing: ["mypy", "pyright where configured"]
    security: ["input validation", "least-privilege creds", "no hardcoded secrets"]
    observability: ["structured logs", "traces", "metrics"]
  workflows:
    - "run lint + tests for code changes"
    - "if docs-only: note 'docs-only' and skip tests"
    - "avoid large refactors unless explicitly requested"
```

## GitHub Workflow Example: Lint & Test Automation
- **Triggers:** `pull_request` (opened, synchronized, reopened), `push` to protected branches, `workflow_dispatch` for manual runs.
- **Quality Gate Job:**
```yaml
name: python-style-and-tests

on:
  pull_request:
    types: [opened, synchronized, reopened]
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
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Lint & Format Check
        run: |
          ruff check .
          black --check .
      - name: Type Check
        run: mypy .
      - name: Tests
        run: pytest --maxfail=1 --disable-warnings --cov
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
- Use Conventional Commits to drive automated versioning, changelog generation, and release tagging.

### Security & Dependency Scanning
```yaml
name: security-and-deps
on:
  schedule:
    - cron: "0 3 * * *"  # daily
  pull_request:
    branches: [main, develop]
  workflow_dispatch: {}

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
  pip-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pip-audit && pip-audit
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

## Contributor Guidelines
- **Proposing Changes:** Open an issue or draft PR with scope, risk, rollout/rollback, and testing plans. Mark docs-only PRs clearly.
- **Review Criteria:** Alignment with architecture decisions, security defaults, logging/observability practices, and coverage targets. No hardcoded secrets or disabled guards.
- **Validation:** Run lint, type checks, and tests; attach logs/coverage to PRs. For infra/data changes, include plan/apply diffs and reproducibility details.

## Troubleshooting & Optimization Tips
- **Copilot/Codex noise:** Narrow context with inline comments/examples; regenerate from canonical modules.
- **Slow CI:** Cache dependencies, split lint/test jobs, parallelize matrices (Python/Node versions, DB backends).
- **Flaky tests:** Seed randomness, isolate fixtures, add timeouts, and quarantine flakes until fixed.
- **Security false positives:** Suppress with justification/expiry; prefer fixing root causes.
- **Observability gaps:** Ensure correlation IDs propagate through async tasks and background workers; add health checks and SLO dashboards.

## Maintenance Schedule
- Review quarterly and after major platform/CI/tooling/security changes; update guardrails post-incident.
- Archive superseded instructions while retaining history for audits; align with Trading Bot Swarm release calendar.

## Closing Note
Standardizing excellence with disciplined Copilot and Codex usage strengthens the reliability, performance, and safety of the Trading Bot Swarm ecosystem.
