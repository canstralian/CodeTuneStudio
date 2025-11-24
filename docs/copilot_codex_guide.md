# GitHub Copilot and Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
This guide standardizes how GitHub Copilot and Codex are configured and used across the Trading Bot Swarm ecosystem to maximize code quality, reliability, performance, and safety. Copilot should operate strictly as a disciplined pair programmer that suggests code aligned with project standards while respecting security and compliance constraints. The scope covers local development, CI/CD, automation rules, and governance for contributions.

## Configuration Overview
- **Testing and linting:** Always run project tests and linters on code changes before merging. Documentation-only changes may skip automated test runs.
- **Code style:** Follow the repository's formatting tools (e.g., `black`, `ruff`, `eslint`, `prettier`) and enforce type checks where applicable.
- **Async patterns:** Prefer async/await for I/O-bound tasks, ensure cancellation support, and avoid blocking calls inside async contexts.
- **Security defaults:** Never hardcode secrets; use environment variables or secret managers. Validate inputs, enforce least privilege for tokens, and enable dependency scanning.
- **Logging and observability:** Use structured logging, correlate logs with request IDs, and emit metrics/traces where supported.
- **CI/CD integration:** Enforce quality gates (lint, test, type check) on pull requests; require branch protection and status checks.
- **Version control:** Use feature branches, meaningful commit messages, and semantic versioning for releases.

## Custom Instruction Behavior for Codex and Copilot
Copilot and Codex should comply with explicit rules that guide suggestions and automations.

### Example Rules
- Prefer explicit imports and typing annotations.
- Suggest secure defaults (parameter validation, timeouts, retries with backoff).
- Avoid generating credentials, PII, or speculative business logic.
- Always propose tests alongside code changes.
- Ignore documentation-only edits when prompting to run tests.

### Conceptual YAML for Custom Instructions
```yaml
copilot:
  role: "Disciplined pair programmer"
  rules:
    - "Follow repository lint/format/type checks."
    - "Suggest test updates for behavioral changes."
    - "Enforce security: no secrets, validate inputs, set timeouts."
    - "Prefer async/await for I/O and avoid blocking patterns."
    - "Use structured logging and propagate correlation IDs."
    - "Skip test prompts for docs-only edits."
    - "Respect code owners and review gates."
  commit_message: "Encourage semantic, meaningful commits"

codex:
  role: "Automation orchestrator"
  rules:
    - "Run lint and tests before merge; allow docs-only bypass."
    - "Ensure branch protection status checks are green."
    - "Keep dependency versions pinned; require scans."
    - "Trigger semantic release on main after quality gate."
    - "Fail fast on secrets exposure or policy violations."
```

## GitHub Workflow Example: Lint and Test Automation
Trigger the workflow on pull requests and protected branches, skipping documentation-only paths.

```yaml
name: quality-gate
on:
  pull_request:
    branches: ["main", "release/*"]
    paths-ignore:
      - "**/*.md"
      - "docs/**"
  push:
    branches: ["main", "release/*"]
    paths-ignore:
      - "**/*.md"
      - "docs/**"

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: |
          black --check .
          ruff check .
      - name: Type check
        run: mypy .
      - name: Test
        run: pytest --maxfail=1 --disable-warnings -q
```

## Semantic Release and Version Tagging Workflow
Use semantic commits and automated release tagging on main after quality gates pass.

```yaml
name: semantic-release
on:
  workflow_run:
    workflows: ["quality-gate"]
    types: ["completed"]
    branches: ["main"]

jobs:
  release:
    permissions:
      contents: write
      issues: write
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install release tooling
        run: npm ci
      - name: Semantic release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

## Security and Dependency Scanning
Automate scanning on a schedule and on pull requests to block vulnerable code.

```yaml
name: security-scan
on:
  schedule:
    - cron: "0 6 * * 1" # Mondays
  pull_request:
    branches: ["main", "release/*"]

jobs:
  sast-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency audit
        run: pip install pip-audit && pip-audit
      - name: SAST
        uses: github/codeql-action/init@v3
        with:
          languages: python
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
```

## Contributor Guidelines
- Propose changes via feature branches and pull requests with clear descriptions.
- Ensure lint, type checks, and tests pass; attach evidence in the PR.
- Follow semantic commit messages and link relevant issues.
- Review criteria: correctness, security posture, performance impact, test coverage, observability, and adherence to style guides.
- Validation: reviewers confirm automated checks are green and code paths are covered by tests; security reviewers sign off on sensitive changes.

## Troubleshooting and Optimization Tips
- **Copilot noise:** Refine prompts with file context and enforce rules from this guide.
- **Flaky tests:** Isolate with `pytest -k` and add retries or deterministic fixtures.
- **Performance regressions:** Use profiling tools and add benchmarks where possible.
- **CI timeouts:** Cache dependencies and parallelize lint/test jobs.
- **False-positive scans:** Suppress with documented allowlists and follow-up fixes.

## Maintenance Schedule
- Review this guide quarterly or after major platform changes.
- Update workflow snippets when tooling versions change or new checks are adopted.
- Validate instructions against current branch protection and CI configurations.

## Closing Note
Standardizing Copilot and Codex behaviors elevates engineering excellence and strengthens the reliability, performance, and safety of the Trading Bot Swarm ecosystem.
