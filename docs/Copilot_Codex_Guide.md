# GitHub Copilot & Codex Configuration Guide for Trading Bot Swarm

## Purpose & Scope
This guide standardizes how GitHub Copilot and Codex are configured and used inside the Trading Bot Swarm ecosystem. Copilot acts strictly as a pair programmer—suggesting patterns but never auto-committing—and follows the behavioral rules and quality gates outlined here. The guide covers:
- Configuration defaults and required project-level settings.
- Coding standards (style, async, security, logging/observability).
- Testing, linting, and CI/CD integration expectations.
- Version control and semantic release practices.
- Contributor workflow, validation, and maintenance expectations.

## Configuration Overview
- **Pair-programming role**: Copilot proposes code but humans own commits and reviews. Suggestions must respect linting, typing, and security baselines before acceptance.
- **Repository config**: Enable Copilot on the repo; disable auto-commit features. Require branch protection with mandatory status checks (lint + tests) before merge.
- **Editor defaults**:
  - Enable inline suggestions but require manual acceptance.
  - Use file-level context limits to avoid leaking secrets or unrelated code.
  - Block suggestions in `.env`, secrets files, and migration outputs.
- **Testing & linting**: Run `pytest`/`coverage`, `ruff` (Python) or equivalent per language. Treat warnings as errors on CI.
- **Code style**: Follow `ruff` + `black` formatting; prefer type hints everywhere. Enforce single-responsibility functions and meaningful docstrings.
- **Async patterns**: Use `asyncio` with `async/await`; avoid blocking calls inside async contexts. Prefer `async with` for resources and structured concurrency (`asyncio.TaskGroup` or `gather` with timeouts).
- **Security defaults**: Never log secrets. Use parameterized queries, validated inputs, and strict dependency pinning. Require secret scanning in CI.
- **Logging & observability**: Standardize on structured logging (`logging` with JSON formatter). Emit traces/metrics hooks (e.g., OpenTelemetry) in critical paths. Include correlation IDs.
- **CI/CD integration**: Lint → test → security scan → build → deploy stages with required checks on PRs. Fail fast on violations.
- **Version control**: Conventional commits; feature branches with scoped PRs; rebase over merge commits when possible.

## Custom Instruction Behavior (Copilot & Codex)
- **General rules**:
  - Suggest minimal diffs and prefer readability over cleverness.
  - Always propose tests alongside code changes; skip only for docs.
  - Avoid generating credentials, tokens, or secrets.
  - Respect project style guides and linters.
- **Example behavioral rules**:
  - Prefer pure functions; avoid global state.
  - Use dependency injection for external services.
  - Validate all external inputs; fail closed.
  - Include structured logs for network/IO operations with redaction of sensitive fields.
- **Full instruction template (conceptual YAML)**:
  ```yaml
  role: "pair_programmer"
  behaviors:
    - prefer_small_diffs: true
    - require_types: true
    - propose_tests: true
    - avoid_secrets: true
    - follow_linters: [black, ruff, mypy]
    - style: pep8_strict
    - async_rules:
        use_asyncio: true
        avoid_blocking_calls: true
        enforce_timeouts: true
    - security:
        input_validation: required
        sql_parameterization: required
        secret_redaction: required
    - logging:
        structured: true
        correlation_id: required
  acceptance_criteria:
    - all_tests_pass: required
    - linters_clean: required
    - docs_only_changes_skip_tests: true
  ```

## Quality Gate Expectations
- **Always run** tests and linters on code changes. Documentation-only changes can skip tests but must still pass spellcheck if configured.
- **Pre-commit** hooks: enable formatting (Black), linting (Ruff), type checks (Mypy), and secret scanning (gitleaks). Reject commits on failure.

## GitHub Workflow Example: Lint & Test Automation
Trigger on pull requests and pushes to main. Quality gate job runs Ruff + Pytest with coverage, then uploads artifacts.

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt || true
      - name: Lint
        run: ruff check .
      - name: Format check
        run: black --check .
      - name: Type check
        run: mypy .
      - name: Run tests
        run: pytest --cov=.
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: ./.coverage
```

## Semantic Release & Version Tagging
- Use conventional commits to drive automated release notes.
- Configure `semantic-release` to create tags, GitHub releases, and changelogs from CI after main branch merges.

```yaml
name: release
on:
  workflow_run:
    workflows: ["ci"]
    types: ["completed"]
    branches: ["main"]
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
          node-version: 20
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Security & Dependency Scanning
- Enable Dependabot for dependency PRs.
- Add CI scanning for secrets, vulnerabilities, and SBOM generation.

```yaml
name: security
on:
  schedule:
    - cron: '0 3 * * *'
  pull_request:
  workflow_dispatch:
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Secret scan
        uses: trufflesecurity/trufflehog@v3
      - name: Dependency audit
        run: pip install pip-audit && pip-audit
      - name: SBOM
        uses: anchore/sbom-action@v0
```

## Contributor Guidelines
- **Proposing changes**: Open an issue or draft PR with scope, risks, and testing plan. Use feature branches and conventional commit messages.
- **Review criteria**: Clarity, adherence to style guides, test coverage, performance considerations, and security posture. Changes without tests should justify explicitly.
- **Validation process**: CI must pass; reviewers validate functionality, observability hooks, and security posture before approval.

## Troubleshooting & Optimization
- **Flaky tests**: Quarantine, add deterministic seeds, improve isolation (e.g., temp DB). Use `pytest -q --maxfail=1` locally.
- **Slow CI**: Cache `pip`/`npm`, parallelize lint/test, and use selective path filters.
- **Copilot noise**: Narrow context, disable in large auto-generated files, and tune file-exclusion rules.
- **Mypy/ruff conflicts**: Prefer typing correctness; adjust ruff ruleset sparingly with inline ignores plus justification.

## Maintenance Schedule
- Quarterly review of this guide to align with current stack and tooling.
- Update CI YAMLs when upgrading Python/Node versions or linters.
- Audit security scanners monthly and refresh blocklists.

---
**Goal:** Standardize excellence—boost reliability, performance, and safety across the Trading Bot Swarm through disciplined automation and peer-quality practices.
