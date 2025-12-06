# GitHub Copilot & Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
- **Goal:** Standardize how GitHub Copilot and Codex operate as disciplined pair-programming copilots across trading services, agents, orchestration layers, and shared libraries.
- **Behavioral posture:** Act as **policy enforcers** that shape suggestions toward correctness, safety, and reviewability. They are pair programmers that must never bypass review, tests, linting, or security controls.
- **Coverage:** Applies to backend services (strategies, executors, risk engines), infra-as-code, CI/CD, and shared SDKs. Excludes non-code docs unless explicitly noted.
- **Principle:** Treat Copilot and Codex as teammates bound by the same standards as human contributors, with explicit prompts to surface risks and request missing context before generating code.

## Configuration Overview
- **Testing defaults:** Always run unit + integration suites for changed components. Require deterministic seeds for stochastic tests and skip flaky markers in CI. Block merges if coverage delta is negative. Allow documentation-only changes to skip tests/linters when the diff contains no code or config files.
- **Linting & style:** Use `black`, `ruff`, and `isort` with repo presets. Enforce type checks (`mypy`/`pyright`) for critical packages. Keep imports explicit; avoid wildcard imports. Prefer pure functions and small, named helpers over inline lambdas in complex logic.
- **Async patterns:** Prefer `asyncio` with structured concurrency (e.g., `asyncio.TaskGroup`). Wrap network calls with timeouts and retries; propagate cancellations; avoid unbounded tasks. Require circuit breakers for exchange/gateway clients.
- **Security defaults:** Enforce principle of least privilege; prefer `pydantic` validation at boundaries; sanitize logs; never log secrets; mandate TLS for external calls; pin dependencies. Default to least-privilege IAM roles and scoped API keys; require secret storage (Vault/Secrets Manager) over env files.
- **Logging & observability:** Standardize on structured logging (`json` logs), OpenTelemetry tracing, and metrics with clear cardinality controls. Correlate request IDs across services. Emit audit events for order lifecycle and risk decisions.
- **CI/CD integration:** All PRs must pass lint, type-check, test, and security gates. Require green pipeline before merge; block force-pushes to main branches. Enforce required status checks and branch protection with linear history.
- **Version control hygiene:** Commit in small logical units, with conventional commits when releasing. Rebase feature branches frequently; avoid committing generated artifacts. Document migrations and backfills in commit messages.

## Custom Instruction Behavior
- **Copilot persona:** Conservative advisor that prioritizes safety, tests, and readability. Declines to suggest code that bypasses auth/validation. Prompts should request tests, types, and comments for complex logic. Treat Copilot as a peer reviewer that surfaces edge cases and insists on quality gates.
- **Codex persona:** Automation-focused assistant that scaffolds tests, CI configs, and refactors while respecting the same safety rails. Avoids destructive commands and confirms irreversible steps in scripts. Treat Codex as a release engineer that keeps automation reproducible and observable.

### Example Rules (applied to both tools)
- Suggest test additions for any code change and remind contributors to run them.
- Default to idempotent infrastructure operations with dry-run modes.
- Prefer dependency upgrades with changelog review and staged rollouts.
- Refuse to generate secrets or hard-coded credentials.
- Highlight security-sensitive areas (signing, key management, trading thresholds) for reviewer attention.
- Encourage observability hooks (tracing spans, structured logs) in new services.
- Nudge contributors to keep PRs small, reviewable, and rebased on latest `main`.

### Conceptual Custom Instructions (YAML)
```yaml
copilot:
  role: "pair-programmer enforcer"
  priorities:
    - uphold_lint_and_tests
    - protect_security_controls
    - prefer_readability
  behaviors:
    suggest_tests: true
    request_context_if_uncertain: true
    block_unsafe_patterns:
      - hardcoded_secrets
      - skipping_validation
      - bypassing_authn_authz
      - ignoring_tests_for_code_changes
  coding_style:
    formatter: black
    linter: ruff
    type_checker: mypy
    max_line_length: 100
    async_guidelines: structured_concurrency
  ci_expectations:
    require_green_pipeline: true
    documentation_only_changes_skip_tests: true
    remind_to_run_local_checks: true

codex:
  role: "automation co-pilot"
  tasks:
    - scaffold_ci
    - refactor_with_tests
    - add_observability_hooks
    - enforce_release_readiness
  safeguards:
    confirm_stateful_changes: true
    avoid_force_operations: true
    ensure_idempotency: true
    enforce_version_pins: true
  review_prompts:
    - "Have tests been added/updated?"
    - "Did lint/type checks run?"
    - "Are secrets handled via env/secret store?"
    - "Did you avoid skipping quality gates for non-doc changes?"
```

## Workflow: Lint and Test Automation
- **Triggers:** Pull requests targeting `main` or `release/*`; scheduled nightly runs; manual dispatch for hotfix validation.
- **Quality gate job:**
  1. Check out repository with full history for versioning logic.
  2. Set up Python version matrix (e.g., 3.10, 3.11) with cache for pip/uv.
  3. Install dependencies with lockfile integrity checks.
  4. Run `ruff`, `black --check`, `isort --check-only`, and `mypy/pyright`.
  5. Execute unit and integration tests with coverage thresholds enforced.
  6. Upload coverage reports and test artifacts.

### Example GitHub Actions Workflow (lint + test)
```yaml
name: quality-gate

on:
  pull_request:
    branches: ["main", "release/*"]
    paths-ignore:
      - "**/*.md"
      - "docs/**"
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch: {}

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          test -f requirements-dev.txt && pip install -r requirements-dev.txt
      - name: Lint
        run: |
          ruff check .
          black --check .
          isort --check-only .
          mypy .
      - name: Test
        run: |
          pytest --maxfail=1 --disable-warnings --cov --cov-report=xml
      - name: Generate summary
        run: |
          coverage xml
          coverage html
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}
          path: coverage.xml
```

## Best Practice Workflows
### Semantic Release & Version Tagging
- Use conventional commits and `semantic-release` (or `python-semantic-release`) to automate versioning and changelog generation.
- Protect main branch; releases cut from `main` only after passing quality gate.
- Tag format: `vMAJOR.MINOR.PATCH`; pre-releases use `-beta.N`.

- Recommended flow: `feature/*` -> PR -> quality gate -> merge to `main` -> semantic release -> tag -> deploy.

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
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install release tooling
        run: pip install python-semantic-release
      - name: Run semantic release
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release publish
```

### Security & Dependency Scanning
- Enable Dependabot for weekly updates and security alerts.
- Add SAST/SCA jobs (e.g., `bandit`, `pip-audit`, `npm audit` where applicable).
- Fail builds on critical vulnerabilities; auto-create issues for findings.
- Include container scanning (`trivy`) and secret scanning (GitHub Advanced Security) where available.

```yaml
name: security-scan
on:
  pull_request:
    branches: ["main", "release/*"]
  schedule:
    - cron: "30 2 * * 1"

jobs:
  sast-and-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install security tools
        run: |
          pip install bandit pip-audit
          curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
      - name: Static analysis
        run: bandit -r .
      - name: Dependency audit
        run: pip-audit --strict
      - name: Container scan
        run: trivy fs --exit-code 1 --severity CRITICAL,HIGH .
```

## Contributor Guidelines
- **Proposing changes:** Open an issue or draft PR outlining scope, risks, and test plan. Link relevant trading strategies/services affected.
- **Review criteria:** Adherence to style/lint rules, test coverage, safety of trading thresholds, resilience of async flows, and observability hooks.
- **Validation process:**
  - Run lint + type checks locally before PR.
  - Add/adjust tests; include fixtures for exchange simulators and risk caps.
  - Ensure CI pipelines are green; re-run failed jobs after fixes.
  - Provide rollout notes and backout steps for deployments.
  - For documentation-only PRs, note the exemption and ensure no code/config touched.

## Troubleshooting & Optimization
- **Copilot noise:** Tighten context by reducing file scope; restate constraints (tests required, no secrets). Disable on generated files.
- **Lint/test flakiness:** Pin tool versions; use deterministic seeds; quarantine flaky tests with issue references.
- **CI performance:** Cache dependencies and `.mypy_cache`; shard tests by marker; parallelize with matrix builds; upload artifacts for failed runs.
- **Security alerts:** Prioritize critical CVEs; apply vendor patches; document mitigations if deferral is necessary.

## Maintenance Schedule
- **Quarterly:** Review formatting/lint/type-check versions; refresh semantic-release config; rotate credentials and tokens.
- **Monthly:** Audit CI durations; prune deprecated workflows; validate coverage thresholds against current codebase.
- **On change:** Update this guide whenever tooling defaults or security baselines shift.

## Closing Note
This guide exists to **standardize excellence**—to keep Copilot, Codex, and contributors aligned on reliability, performance, and safety. Consistent adherence strengthens the trading ecosystem’s integrity and resilience. Treat this guide as a living contract for engineering excellence.
