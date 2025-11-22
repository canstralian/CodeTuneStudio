# GitHub Copilot & Codex Configuration Guide for the Trading Bot Swarm

## Purpose & Scope
This guide standardizes the behavior, configuration, and automation policies for GitHub Copilot and Codex within the Trading Bot Swarm ecosystem. Copilot is treated as a disciplined pair-programmer whose suggestions must respect strict behavioral rules, security defaults, and quality gates. Engineers, ML researchers, and automation services use this document to ensure consistent tooling setup, reliable code generation, and auditable workflows across the portfolio of trading services.

The scope covers:
- Local development environments (IDEs, editors, terminals, containerized setups).
- CI/CD pipelines that lint, test, secure, and release trading bot components.
- Automation scripts that interact with repositories, secrets, and infrastructure.
- Contributor practices that keep code quality, safety, and observability aligned with organizational standards.

## Configuration Overview

### Behavioral Model for Copilot as Pair Programmer
- **Role:** Copilot supplements human authors with suggestion drafts; humans retain final responsibility.
- **Boundaries:** Copilot must never bypass review processes, alter infrastructure credentials, or commit directly to protected branches.
- **Suggestion Acceptance:** Treat Copilot output as untrusted until verified against the quality checklist (tests, linting, security scans).
- **Auditability:** Ensure IDE telemetry and Copilot session logs respect compliance policies; use enterprise features where available.

### Testing & Linting Expectations
- Unit tests run via `pytest` and integration tests through `pytest -m integration` or orchestrated workflows.
- Linters: `ruff` for static analysis, `mypy` for type checking, `black` for formatting (line length 88, target Python 3.10+).
- Always stage changes only after tests and linters pass locally; automated pre-commit hooks enforce the same.

### Code Style & Patterns
- Adopt PEP 8 + Black formatting; no manual deviations unless explicitly configured.
- Prefer dataclasses for immutable configuration objects and `pydantic` models for validation.
- Async services must use `asyncio` with `async/await`, structured concurrency (`asyncio.TaskGroup`), and graceful shutdown hooks.
- Keep functions pure where feasible; isolate side effects in adapters or orchestrators.

### Security Defaults
- Default-deny approach to secrets; load from environment or vault, never hard-code.
- Enforce principle of least privilege for API keys and database credentials.
- Mandate dependency scanning (Snyk, pip-audit) and supply chain verification.
- Require threat modeling for bots that execute automated trades or handle capital movements.

### Logging & Observability
- Use structured logging (`structlog` or `logging` with JSON formatter) tagged with bot identifier, environment, and correlation IDs.
- Export metrics via OpenTelemetry; standard metrics: trade latency, success/failure counts, risk rule triggers.
- Aggregate traces and logs in centralized monitoring; define SLOs for trading latency and error budget policies.

### CI/CD Integration
- CI must validate every PR with lint, test, security, and dependency checks.
- CD pipelines follow staged rollouts: canary -> shadow -> production.
- Versioning uses semantic release with automated changelog generation and Git tags.

### Version Control Practices
- Main branch protected; require PR reviews, status checks, and signed commits where possible.
- Feature branches named `feature/<ticket>`, bugfix branches `fix/<ticket>`.
- Squash merges default; ensure commit messages reflect user-facing change intent.

## Custom Instruction Behavior for Codex & Copilot

### Instruction Layers
1. **Global Defaults:** Security, quality, and compliance standards that apply to every repository.
2. **Repository-Level Overrides:** Specific linters, test suites, or infrastructure contexts.
3. **Task-Level Rules:** Instructions set per issue or PR, including acceptance criteria.

### Example Behavioral Rules
- Prefer explicit imports; avoid wildcard imports.
- Always add docstrings for public functions/classes.
- Treat asynchronous operations as first-class; avoid blocking calls in async contexts.
- Run `pytest`, `ruff`, `black`, and `mypy` after code changes; skip only when documentation-only change.
- Never include secrets, tokens, or credentials in code, comments, or logs.
- If tests require external systems, use mocks or staging endpoints.

### Conceptual YAML Configuration
```yaml
copilot:
  role: "pair_programmer"
  behaviors:
    - "Follow security defaults; never suggest secret values."
    - "Align suggestions with repo lint/test configuration."
    - "Provide unit test scaffolding for new logic."
    - "Favor async patterns (`async/await`, `TaskGroup`) in services."
  acceptance_criteria:
    tests_required: true
    linters_required: ["black", "ruff", "mypy"]
    docs_only_exemption: true
    security_checks: ["pip-audit", "safety"]

codex:
  mode: "automation_assistant"
  policies:
    - "Obey task-specific instructions from AGENTS.md or issue templates."
    - "Refuse to modify protected branches directly."
    - "Log reasoning steps in PR descriptions when automation executes changes."
  execution_pipeline:
    pre_commit:
      - "black ."
      - "ruff check ."
      - "pytest"
    post_commit:
      - "mypy"
      - "pip-audit"
```

### Testing & Linting Requirements
- All code-generating tasks must run the test and lint suite before requesting review.
- Documentation-only changes (README updates, markdown edits) may bypass automated tests but require review confirmation that no code paths are affected.

## GitHub Workflow: Lint & Test Automation
```yaml
name: quality-gate

on:
  pull_request:
    branches: ["main", "release/*"]
    paths-ignore:
      - "**/*.md"
      - "docs/**"
  push:
    branches: ["main"]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install black==23.12.1 ruff mypy pytest pip-audit

      - name: Lint (Black)
        run: black --check .

      - name: Lint (Ruff)
        run: ruff check .

      - name: Type Check (mypy)
        run: mypy .

      - name: Run Tests
        run: pytest --maxfail=1 --disable-warnings -q

      - name: Dependency Audit
        run: pip-audit
```

## Semantic Release & Version Tagging

### Best Practice Workflow
```yaml
name: semantic-release

on:
  push:
    branches: ["main"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install semantic-release
        run: npm install -g semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/github

      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release
```
- Commits must follow Conventional Commit semantics (`feat:`, `fix:`, `chore:`, etc.).
- semantic-release updates CHANGELOG.md, creates Git tags, and publishes GitHub releases automatically.

## Security & Dependency Scanning Workflow
```yaml
name: security-scan

on:
  schedule:
    - cron: "0 6 * * 1"   # Weekly Monday scan
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - name: Install tools
        run: |
          python -m pip install --upgrade pip
          pip install pip-audit safety bandit
      - name: pip-audit
        run: pip-audit
      - name: Safety
        run: safety check
      - name: Bandit
        run: bandit -r .
```
- Integrate findings with issue tracking; prioritize critical/high vulnerabilities.
- Consider adding container scanning (Trivy) for Docker images.

## Contributor Guidelines
### Proposing Changes
1. Create an issue detailing the problem or feature with acceptance criteria and risk assessment.
2. Fork or branch from `main`; keep changes scoped and atomic.
3. Document architecture decisions in ADRs when altering core trading logic or infrastructure.

### Review Criteria
- Tests cover new logic and maintain >90% coverage for critical modules.
- Lint, type check, and security scans pass with no new warnings.
- Observability hooks (metrics, logs) updated when behavior changes.
- Deployment scripts and runbooks reflect operational adjustments.

### Validation Process
- Execute local quality gate (lint, tests, security).
- Obtain at least one reviewer from trading core team; security-sensitive changes need security engineer sign-off.
- Merge via squash once status checks and approvals are complete.

## Troubleshooting & Optimization Tips
- **Copilot not respecting rules:** Re-sync enterprise policies, ensure latest Copilot extension version, review custom instructions in IDE settings.
- **Flaky tests:** Use `pytest -n auto` with `pytest-rerunfailures`; log random seeds and environment variables.
- **Slow lint/test runs:** Enable caching (`ruff --cache`, `pytest --lf --ff`), leverage pre-commit with `--hook-stage manual` for selective runs.
- **Semantic-release failures:** Ensure `GITHUB_TOKEN` has write permissions and Conventional Commit messages are valid.
- **Security scan noise:** Configure baseline files for Bandit/Safety to ignore vetted false positives but review regularly.

## Maintenance Schedule
- **Quarterly:** Review tool versions (Black, Ruff, mypy, semantic-release) and update configuration.
- **Monthly:** Validate CI workflows, update dependency scan baselines, verify secrets rotation.
- **Per Release:** Confirm observability dashboards and runbooks match deployed bot behaviors.
- Record changes to this guide in CHANGELOG with dates and responsible maintainers.

---

By following these standards, the Trading Bot Swarm maintains excellence in engineering practices, reinforcing the reliability, performance, and safety of its automated trading ecosystem.
