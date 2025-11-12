# GitHub Copilot & Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
This guide establishes a uniform framework for configuring GitHub Copilot and Codex within the Trading Bot Swarm ecosystem. It ensures that AI pair-programming assistance operates under strict behavioral rules aligned with the project's security, reliability, and performance goals. Copilot acts as a disciplined collaborator that reinforces coding standards, automates quality checks, and safeguards trading strategies. Codex complements Copilot by executing automation scripts under the same rigorously defined expectations. Together, they help standardize excellence across all services, plugins, and infrastructure components in the swarm.

## Configuration Overview
- **Testing & Quality Gates**: All code changes must include unit/integration tests and pass automated suites before merging. Copilot suggestions should prompt developers to add or update relevant tests.
- **Linting & Static Analysis**: Enforce style and correctness using tools like `flake8`, `black`, `isort`, `mypy`, or project-specific linters. Copilot should default to lint-compliant code snippets.
- **Code Style**: Prefer explicit imports, type hints, immutable defaults, and functional purity in async flows. Align with `PEP 8` plus project-specific conventions from `setup.cfg` or `pyproject.toml`.
- **Async Patterns**: Default to `asyncio`-friendly patterns with proper cancellation handling. Encourage `async with` and `async for` usage, and ensure background tasks are supervised.
- **Security Defaults**: Enforce principle of least privilege, sanitize all external inputs, avoid hard-coded secrets, and leverage vault/secret managers. Copilot should flag risky patterns.
- **Logging & Observability**: Standardize structured logging (`logging` or `structlog`), include correlation IDs, and export metrics/traces via OpenTelemetry where available.
- **CI/CD Integration**: Ensure automated pipelines run lint, test, build, and deploy steps. Copilot suggestions must be compatible with workflow requirements.
- **Version Control**: Require descriptive branch names, atomic commits, and signed tags. Codex automations must never bypass review policies.

## Custom Instruction Behavior
Codex and Copilot should operate with a shared rule set that reinforces disciplined engineering practices.

### Behavioral Rules (Examples)
1. Always propose tests for new or modified logic.
2. Assume linting and type-checking will run; generate code that satisfies both.
3. Avoid introducing dependencies without updating manifests.
4. Prefer secure defaults and validate external data rigorously.
5. Highlight potential performance or concurrency issues.
6. Respect documentation vs. code change policies (tests/linters not required for docs-only changes).
7. Encourage incremental commits with clear messages and reference related issues when applicable.

### Conceptual YAML for Custom Instructions
```yaml
copilot:
  role: "Disciplined pair programmer"
  focus:
    - enforce_tests: true
    - encourage_linting: true
    - security_default: "least_privilege"
    - async_patterns: "supervised_tasks_only"
    - logging: "structured"
  guidelines:
    suggest_tests: "Always add/modify tests for code changes."
    lint_style: "Conform to PEP8 + project tooling."
    secrets: "Never generate hard-coded secrets."
    review_ready: "Changes must be merge-ready with passing CI."
codex:
  role: "Automation orchestrator"
  focus:
    - ci_cd_enforcement: true
    - dependency_sync: true
    - security_audit: true
  guidelines:
    respect_approvals: "Never bypass human code review."
    run_quality_gates: "Execute tests, linters, and scanners before merge."
    docs_only_changes: "Skip heavy checks only when code is untouched."
shared:
  version_control:
    commit_style: "Atomic, descriptive, signed when possible"
    branch_convention: "feature/<scope>/<ticket>"
  observability:
    logs: "structured_json"
    metrics: "opentelemetry"
```

## Testing and Linting Expectations
- Run `pytest`, linters, and type-checkers before opening a pull request.
- Document-only changes may bypass heavy test suites but must pass spelling and link checks if configured.
- Use pre-commit hooks to enforce formatting and security scans (e.g., `pre-commit run --all-files`).

## GitHub Workflow: Lint and Test Automation
Trigger on pull requests targeting `main` or `release/*` branches and on pushes to `main`.

```yaml
name: CI Quality Gate

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main", "release/*"]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: |
          black --check .
          isort --check-only .
          flake8
          mypy

      - name: Run tests
        run: |
          pytest --maxfail=1 --disable-warnings -q

      - name: Upload coverage
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
```

## Semantic Release & Version Tagging Workflow
Adopt automated semantic versioning triggered after successful quality gates.

```yaml
name: Release

on:
  workflow_run:
    workflows: ["CI Quality Gate"]
    types:
      - completed

jobs:
  semantic-release:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install semantic-release
        run: npm install -g semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/github
      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release
```

## Security & Dependency Scanning Workflow
Integrate continuous scanning to detect vulnerabilities and outdated packages.

```yaml
name: Security Scan

on:
  schedule:
    - cron: "0 6 * * 1"  # Weekly Monday run
  pull_request:
    branches: ["main", "release/*"]

jobs:
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install tools
        run: |
          python -m pip install --upgrade pip
          pip install pip-audit safety bandit
      - name: Dependency audit
        run: pip-audit
      - name: Security lint
        run: bandit -r core plugins utils
      - name: Publish report
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: reports/security/
```

## Contributor Guidelines
- **Proposing Changes**: Open an issue describing the trading strategy, infrastructure update, or tooling enhancement. Outline risks, dependencies, and test plans.
- **Review Criteria**: Pull requests must demonstrate passing CI, updated documentation, adherence to security policies, and comprehensive tests. Reviewers focus on correctness, performance impact, fault tolerance, and observability coverage.
- **Validation Process**: Use staging environments to run end-to-end trading simulations before production deployment. Capture metrics, logs, and anomaly reports.

## Troubleshooting & Optimization Tips
- **Copilot Suggestions Drift**: Regenerate completions after updating configuration files or run a short diff review to enforce style.
- **Failing Tests**: Reproduce locally with `pytest -vv` and enable verbose logging. Use feature flags to isolate modules.
- **Lint Failures**: Run `black . && isort .` to auto-format; address `flake8` and `mypy` errors manually.
- **CI Timeouts**: Parallelize test suites, cache dependencies, or split workflows into matrix jobs.
- **Security Alerts**: Prioritize critical CVEs, patch dependencies, and document mitigations.

## Maintenance Schedule
- **Quarterly Review**: Update Copilot/Codex instructions, tooling versions, and workflow triggers.
- **Monthly Audit**: Verify CI logs, check dependency freshness, and rotate secrets.
- **Per Release**: Validate semantic versioning rules, ensure release notes are accurate, and confirm security reports are archived.

---

By institutionalizing these configurations and practices, the Trading Bot Swarm ecosystem standardizes excellence, strengthening reliability, performance, and safety across all automated trading operations.
