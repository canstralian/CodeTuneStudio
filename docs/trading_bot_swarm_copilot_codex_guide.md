# Trading Bot Swarm Copilot & Codex Configuration Guide

## Purpose and Scope
- Establish a consistent, secure, and high-quality engineering baseline for the Trading Bot Swarm ecosystem.
- Position GitHub Copilot as a **strict pair programmer**: it should propose code that matches project standards, but humans own final decisions and must review every change.
- Ensure Codex automations follow the same rules, enabling reliable code generation, reviews, and CI/CD orchestration across services and plugins.

## Configuration Overview
- **Testing & Coverage:** Always run relevant unit/integration tests for code changes; skip only pure documentation edits. Enforce coverage thresholds via CI, and block merges on failing tests.
- **Linting & Style:** Use Ruff/Black formatting defaults; follow project typing and docstring conventions. Reject auto-generated code that disables lint rules without justification.
- **Async Patterns:** Prefer `asyncio`/`aiohttp` for I/O-bound tasks; avoid blocking calls inside async code. Wrap external calls with timeouts and circuit breakers.
- **Security Defaults:** Apply least privilege for secrets; never log secrets or tokens. Require dependency pinning, vetted third-party libraries, and static analysis for secrets/credentials.
- **Logging & Observability:** Standardize structured logging (JSON or key-value) with correlation IDs. Emit metrics for latency, error rates, and throughput. Add tracing spans for network/database calls.
- **CI/CD Integration:** All pushes and PRs trigger lint + test gates. Require signed commits/tags for releases. Use protected branches with mandatory status checks.
- **Version Control Hygiene:** Small, focused commits with meaningful messages. Avoid committing generated artifacts. Keep feature branches rebased on main.

## Custom Instruction Behavior
Copilot and Codex share a unified rule set to reduce drift between human and automated contributions.

### Example Behavioral Rules
- Never invent APIs; prefer existing utilities under `core/`, `utils/`, `components/`, or `plugins/`.
- Prefer pure functions and idempotent operations; avoid hidden side effects.
- Add tests alongside new logic and update snapshots/fixtures as needed.
- Defer to project security policies (secrets, auth, network access) before suggesting integrations.
- Decline to auto-merge; always request human review.

### Conceptual YAML for Custom Instructions
```yaml
copilot:
  role: "pair_programmer"
  principles:
    - follow_project_standards: true
    - block_on_missing_tests: true
    - no_doc-only_enforcement: false  # documentation-only changes skip mandatory test runs
    - avoid_new_dependencies: true
    - respect_security_policies: true
  code_quality:
    lint: ["ruff check .", "ruff format --check ."]
    tests: ["pytest"]
    type_check: ["mypy core/ utils/ components/"]
  behaviors:
    - never bypass code review
    - propose minimal diffs, prefer clarity over cleverness
    - include logging, metrics, and error handling that fit observability standards

codex:
  role: "automation_guardian"
  principles:
    - enforce_branch_protection: true
    - require_status_checks: ["lint", "test", "type-check"]
    - no_automerge_on_red: true
    - ignore_doc_only_for_tests: true  # docs skip test enforcement
  workflows:
    pr_validation:
      steps: ["checkout", "setup-python", "install-deps", "ruff", "pytest", "mypy"]
    release:
      steps: ["semantic-release", "tag", "publish-artifacts"]
```

## GitHub Workflow Example: Lint & Test Automation
Trigger on pull requests and pushes to protected branches. Skip when only documentation files change.

```yaml
name: quality-gate

on:
  push:
    branches: [main, release/*]
  pull_request:
    branches: [main, release/*]
  workflow_call:

jobs:
  lint-and-test:
    if: ${{ !contains(github.event.head_commit.message, '[skip ci]') }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint
        run: |
          ruff check .
          ruff format --check .

      - name: Tests
        run: pytest --maxfail=1 --disable-warnings -q

      - name: Type check
        run: mypy core/ utils/ components/
```

## Semantic Release & Version Tagging
- Use semantic commit messages (feat, fix, chore, docs, refactor, perf, test).
- Automate releases from `main` after passing quality gates.
- Signed tags and changelog generation are mandatory; publish to package registry when applicable.

```yaml
name: semantic-release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install release tooling
        run: npm ci

      - name: Semantic release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

## Security & Dependency Scanning
- Enforce dependency pinning and automated vulnerability checks.
- Require secret scanning on every push/PR.

```yaml
name: security-scan

on:
  push:
  pull_request:

jobs:
  deps-and-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Dependency audit
        run: pip install pip-audit && pip-audit

      - name: Secret scan
        uses: github/super-linter@v6
        env:
          VALIDATE_ALL_CODEBASE: true
          DEFAULT_BRANCH: main
          FILTER_REGEX_EXCLUDE: "docs/.*|*.md"
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Contributor Guidelines
- Open an issue or discussion describing the proposal and impact.
- For code changes, provide linked tests, lint results, and rationale for design and security implications.
- Review criteria: correctness, test coverage, observability, security posture, performance, adherence to style guides.
- Validation: reviewers rerun lint/tests; CI must be green before merge; releases require signed tags and changelog entries.

## Troubleshooting & Optimization Tips
- **Copilot noise:** tighten prompts with file context; disable suggestions on generated files.
- **Flaky tests:** add retries with backoff for external calls; improve fixture isolation; parallelize with `pytest -n auto` when stable.
- **Async bottlenecks:** profile event loops; replace blocking I/O; add timeouts and fallbacks for third-party APIs.
- **CI timeouts:** cache dependencies; split lint/test/type-check into parallel jobs; run quick linters before heavier suites.
- **False-positive secret scans:** add narrow allowlists with regex comments and rotate tokens proactively.

## Maintenance Schedule
- Quarterly review to align with updated security baselines, dependency versions, and CI templates.
- Update YAML snippets after any CI pipeline change or new tool adoption.
- Archive superseded instructions and link to current guide versions.

## Closing Note
Standardizing Copilot and Codex behavior raises the reliability, performance, and safety of the Trading Bot Swarm ecosystem, ensuring every change meets the same bar of excellence.
