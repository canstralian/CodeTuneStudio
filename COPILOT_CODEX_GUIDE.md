# GitHub Copilot & Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
- **Goal:** Standardize how GitHub Copilot and Codex operate as disciplined pair-programming copilots across trading services, agents, orchestration layers, and shared libraries.
- **Behavioral posture:** Assist with suggestions, but never bypass review, tests, linting, or security controls. Copilot must be a **policy enforcer**, not merely an autocomplete.
- **Coverage:** Applies to backend services (strategies, executors, risk engines), infra-as-code, CI/CD, and shared SDKs. Excludes non-code docs unless explicitly noted.

## Configuration Overview
- **Testing defaults:** Always run unit + integration suites for changed components. Require deterministic seeds for stochastic tests and skip flaky markers in CI. Block merges if coverage delta is negative.
- **Linting & style:** Use `black`, `ruff`, and `isort` with repo presets. Enforce type checks (`mypy`/`pyright`) for critical packages. Keep imports explicit; avoid wildcard imports.
- **Async patterns:** Prefer `asyncio` with structured concurrency (e.g., `asyncio.TaskGroup`). Wrap network calls with timeouts and retries; propagate cancellations; avoid unbounded tasks.
- **Security defaults:** Enforce principle of least privilege; prefer `pydantic` validation at boundaries; sanitize logs; never log secrets; mandate TLS for external calls; pin dependencies.
- **Logging & observability:** Standardize on structured logging (`json` logs), OpenTelemetry tracing, and metrics with clear cardinality controls. Correlate request IDs across services.
- **CI/CD integration:** All PRs must pass lint, type-check, test, and security gates. Require green pipeline before merge; block force-pushes to main branches.
- **Version control hygiene:** Commit in small logical units, with conventional commits when releasing. Rebase feature branches frequently; avoid committing generated artifacts.

## Custom Instruction Behavior
- **Copilot persona:** Conservative advisor that prioritizes safety, tests, and readability. Declines to suggest code that bypasses auth/validation. Prompts should request tests, types, and comments for complex logic.
- **Codex persona:** Automation-focused assistant that scaffolds tests, CI configs, and refactors while respecting the same safety rails. Avoids destructive commands and confirms irreversible steps in scripts.

### Example Rules (applied to both tools)
- Suggest test additions for any code change.
- Default to idempotent infrastructure operations.
- Prefer dependency upgrades with changelog review.
- Refuse to generate secrets or hard-coded credentials.
- Highlight security-sensitive areas (signing, key management, trading thresholds) for reviewer attention.

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
  coding_style:
    formatter: black
    linter: ruff
    type_checker: mypy
    max_line_length: 100
    async_guidelines: structured_concurrency
  ci_expectations:
    require_green_pipeline: true
    documentation_only_changes_skip_tests: true

codex:
  role: "automation co-pilot"
  tasks:
    - scaffold_ci
    - refactor_with_tests
    - add_observability_hooks
  safeguards:
    confirm_stateful_changes: true
    avoid_force_operations: true
    ensure_idempotency: true
  review_prompts:
    - "Have tests been added/updated?"
    - "Did lint/type checks run?"
    - "Are secrets handled via env/secret store?"
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
      - name: Lint
        run: |
          ruff check .
          black --check .
          isort --check-only .
          mypy .
      - name: Test
        run: |
          pytest --maxfail=1 --disable-warnings --cov --cov-report=xml
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
      - name: Static analysis
        run: bandit -r .
      - name: Dependency audit
        run: pip-audit --strict
```

## Contributor Guidelines
- **Proposing changes:** Open an issue or draft PR outlining scope, risks, and test plan. Link relevant trading strategies/services affected.
- **Review criteria:** Adherence to style/lint rules, test coverage, safety of trading thresholds, resilience of async flows, and observability hooks.
- **Validation process:**
  - Run lint + type checks locally before PR.
  - Add/adjust tests; include fixtures for exchange simulators and risk caps.
  - Ensure CI pipelines are green; re-run failed jobs after fixes.
  - Provide rollout notes and backout steps for deployments.

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
Standardizing Copilot and Codex behavior—and the guardrails around them—strengthens reliability, performance, and safety for the Trading Bot Swarm. Treat this guide as a living contract for engineering excellence.
