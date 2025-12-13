# ⚠️ DEPRECATED - This document has been archived

**This guide has been superseded by the current documentation:**
- **For developers**: See [`docs/ai-assistant-guide.md`](../../ai-assistant-guide.md)
- **For AI agents**: See [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md)

This file is preserved for historical reference only and contains outdated information, including references to non-existent projects ("Trading Bot Swarm").

---

# GitHub Copilot and Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
This guide defines how GitHub Copilot and Codex act as disciplined pair programmers across the Trading Bot Swarm ecosystem. It documents the behavioral rules, tooling configuration, automation workflows, and validation steps that keep code quality, security, and reliability consistently high. Copilot and Codex should always reinforce project conventions rather than invent their own.

## Configuration Overview
- **Testing and linting**: Run the full lint and test suite for any code change; documentation-only changes may skip execution but still require a quick format check. Favor `pytest` and project-standard linters (e.g., Ruff/Flake8/ESLint) with strict error thresholds.
- **Code style**: Enforce Black/Prettier-style formatting, typed Python where applicable (mypy/pyright), and explicit imports. Avoid try/except around imports. Prefer small, composable functions and consistent naming aligned with existing modules.
- **Async patterns**: Use `asyncio` primitives, `async with` for resources, and cancel tasks cleanly. Never block the event loop with synchronous I/O; prefer `await`able calls and timeouts.
- **Security defaults**: Deny-by-default network calls, sanitize inputs, validate schemas, and keep secrets out of logs. Require dependency pinning and vulnerability scanning before merges. Enable branch protection and required status checks.
- **Logging and observability**: Use structured logging (JSON-friendly) with correlation IDs. Emit metrics for critical paths and instrument traces for long-lived async tasks. Avoid sensitive payloads in logs.
- **CI/CD integration**: Require lint, type-check, and test jobs to pass before merge. Enforce review approvals and signed commits for release branches. Publish artifacts only after quality gates succeed.
- **Version control**: Use conventional commits, short-lived branches, and rebase over merge when possible. Keep PRs small, labeled with scope, and linked to issues. Auto-close stale branches after review or inactivity.

## Custom Instruction Behavior for Codex and Copilot

### Behavioral Rules (examples)
- Treat Copilot as a guardrailed assistant: propose changes that align with project patterns, add tests for new logic, and avoid speculative refactors.
- Prefer clarity over brevity: include docstrings and type hints, and add comments around risk boundaries (e.g., external API calls, trading algorithms).
- Never commit secrets, credentials, or example keys. Mask sensitive values in logs and configs.
- For code changes, always run or recommend running tests and linters; skip automation only for documentation-only edits.

### Conceptual Custom Instructions (YAML)
```yaml
copilot:
  role: "pair-programmer with strict guardrails"
  must_do:
    - follow repository coding standards and async guidelines
    - suggest tests and lint checks for any code change
    - minimize external calls; use mocks in tests
    - keep prompts and completions free of secrets
  must_not_do:
    - generate untyped code when the module is typed
    - auto-create large refactors without explicit request
    - bypass code review or CI requirements
  reviewer_notes:
    - highlight missing tests, logging, or security validations
    - flag blocking operations inside async flows

codex:
  role: "automation copilot for CI/CD and maintenance"
  must_do:
    - enforce quality gates (lint, type, test) on code diffs
    - ignore documentation-only changes for heavy test runs
    - recommend dependency and security updates regularly
  must_not_do:
    - push releases without passing gates
    - downgrade security settings for speed
```

## GitHub Workflow: Lint and Test Automation
Trigger on pull requests to `main` and on pushes to release branches. Use `paths-ignore` to skip docs-only changes.

```yaml
name: quality-gate

on:
  pull_request:
    branches: [main]
    paths-ignore:
      - "docs/**"
      - "**/*.md"
  push:
    branches: ["release/*"]
    paths-ignore:
      - "docs/**"
      - "**/*.md"

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          mypy .
      - name: Test
        run: pytest --maxfail=1 --disable-warnings -q
```

## Best-Practice Workflows

### Semantic Release and Version Tagging
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
      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

### Security and Dependency Scanning
```yaml
name: security-scan

on:
  schedule:
    - cron: "0 6 * * 1"  # weekly
  workflow_dispatch: {}

jobs:
  dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Python dependency audit
        run: pip install pip-audit && pip-audit

  codeql:
    uses: github/codeql-action/.github/workflows/codeql.yml@v3
    secrets: inherit
```

## Contributor Guidelines
- Propose changes via issues and scoped branches; use conventional commit messages.
- Every PR must show passing lint/type/test checks and include risk-aware notes for trading logic changes.
- Reviewers check for test coverage, logging/observability hooks, secure defaults, and adherence to async and style rules.
- Validation includes CI results, manual verification of critical paths, and ensuring no secrets or credentials are present.

## Troubleshooting and Optimization
- **Flaky tests**: isolate with `pytest -k` selectors; add retries only at the fixture level and document root causes.
- **Lint failures**: run formatters locally (`black`, `ruff`, `prettier`) and align imports. Enable editor integrations to auto-fix on save.
- **Slow CI**: cache dependencies, parallelize test matrices, and use `paths-ignore` to skip non-code changes.
- **Async issues**: check for blocking calls, missing awaits, and unhandled cancellations; add timeouts and structured logging to trace flows.
- **Security alerts**: rotate credentials immediately, upgrade affected packages, and document mitigations in the changelog.

## Maintenance Schedule
- Review this guide quarterly or whenever CI/CD, security posture, or coding standards change.
- Keep workflow versions and action pins current; audit third-party actions for provenance.
- Archive superseded instructions and link to the latest guidance to avoid drift across trading-bot repositories.

## Closing Note
Standardizing excellence in Copilot and Codex behavior strengthens the reliability, performance, and safety of the Trading Bot Swarm ecosystem.
