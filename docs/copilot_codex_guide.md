# GitHub Copilot & Codex Configuration Guide for Trading Bot Swarm

## Purpose and Scope
- Establish a consistent, secure, and high-quality development experience by treating Copilot and Codex as disciplined pair programmers.
- Standardize automation and CI/CD practices for the Trading Bot Swarm ecosystem, ensuring reliable trading agents, orchestration services, and infrastructure components.
- Provide actionable steps to configure, run, and maintain automation that enforces testing, linting, security, and release standards.

## Configuration Overview
- **Pair-programmer role:** Copilot (and Codex) must propose minimal, auditable changes, avoid speculative code, and preserve existing safety controls.
- **Testing & linting:** Always run unit/integration tests and linters for code changes; documentation-only changes may skip.
- **Code style:** Follow project formatters (e.g., Black/ruff for Python, Prettier/ESLint for JS). Enforce type hints and explicit async patterns.
- **Async patterns:** Prefer structured concurrency; avoid fire-and-forget. Use timeouts, cancellation, and bounded retries.
- **Security defaults:** Validate inputs, sanitize logs, least-privilege for secrets/tokens, and forbid hard-coded credentials or PII.
- **Logging & observability:** Use structured logging with correlation IDs; emit metrics for critical paths; guard against log noise and leakage.
- **CI/CD integration:** Quality gates must block merges if tests, linters, or security scans fail. Require PR status checks.
- **Version control:** Small, atomic commits with descriptive messages; keep feature branches rebased; avoid committing generated artifacts.

## Custom Instruction Behavior (Copilot & Codex)
- **Principles:**
  - Respect safety rails and existing architecture.
  - Prefer incremental edits over large rewrites; propose diffs that retain context.
  - Never invent APIs, data sources, or environment variables without references.
  - Always surface test commands for suggested changes and note when tests are skipped.
- **Example rules:**
  - Do not suggest code that bypasses authentication, authorization, or rate limits.
  - Default to defensive error handling and explicit timeouts.
  - Use project logging helpers; avoid print debugging.
  - When unsure, ask for clarification instead of guessing behavior.

### Conceptual YAML for Custom Instructions
```yaml
copilot:
  role: "Disciplined pair programmer for Trading Bot Swarm"
  rules:
    - "Use minimal diffs; preserve safety and compliance controls"
    - "Require tests/linters for code changes; documentation-only changes may skip"
    - "Follow project formatters and typing standards"
    - "Propose structured async with timeouts and cancellation"
    - "Never suggest hard-coded secrets or PII"
    - "Use structured logging and metrics; avoid print statements"
    - "State test commands in suggestions; mark if not run"
    - "Ask for clarification when requirements are ambiguous"
codex:
  role: "Automation assistant enforcing quality gates"
  rules:
    - "Run linters and tests before merge"
    - "Reject suggestions that reduce security posture"
    - "Align with CI/CD workflows and release/versioning policies"
```

## GitHub Workflow: Lint & Test Automation
- **Trigger conditions:** On pull requests to `main` and pushes to `main` affecting source, tests, workflows, or configuration; ignore documentation-only paths.
- **Quality gate steps:**
  1. Checkout code with full history for semantic versioning.
  2. Set up languages (e.g., Python/Node) with cached dependencies.
  3. Install dependencies (including dev extras) and tools.
  4. Run linters/format checks (e.g., `ruff check`, `black --check`, `eslint`, `prettier --check`).
  5. Run tests with coverage (e.g., `pytest --maxfail=1 --disable-warnings --cov`).
  6. Upload coverage artifacts and test results for visibility.

```yaml
name: lint-and-test
on:
  push:
    branches: [main]
    paths-ignore:
      - '**/*.md'
      - 'docs/**'
  pull_request:
    branches: [main]
    paths-ignore:
      - '**/*.md'
      - 'docs/**'
jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install Python deps
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Install Node deps
        run: npm ci
      - name: Lint (Python)
        run: ruff check . && black --check .
      - name: Lint (JS/TS)
        run: npm run lint && npm run format:check
      - name: Tests
        run: pytest --maxfail=1 --disable-warnings --cov
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage*
```

## Semantic Release & Version Tagging
- Use conventional commits to drive automated versioning.
- Require changelog generation and git tags per release.
- Guardrail: Releases only from `main` after successful quality gates.

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
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

## Security & Dependency Scanning
- Run dependency audits and SAST in CI; block merges on critical findings.
- Rotate and scope secrets; use GitHub environments with required approvals for production deploys.

```yaml
name: security-scan
on:
  schedule:
    - cron: '0 6 * * *'
  pull_request:
    branches: [main]
jobs:
  deps-and-sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Dependency Audit (Python)
        run: pip install pip-audit && pip-audit
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Dependency Audit (Node)
        run: npm audit --audit-level=high
      - name: CodeQL Init
        uses: github/codeql-action/init@v3
        with:
          languages: 'javascript,python'
      - name: CodeQL Analyze
        uses: github/codeql-action/analyze@v3
```

## Contributor Guidelines
- **Proposing changes:** Open a GitHub issue or discussion first for significant updates. Provide context, risk assessment, and rollout plan.
- **Review criteria:**
  - Adherence to security defaults and logging/observability practices.
  - Tests and linters executed with evidence (links to runs or local logs).
  - Clear, minimal diffs with descriptive commit messages.
  - Compliance with async patterns, error handling, and formatting standards.
- **Validation process:**
  - Automated quality gate must pass.
  - Manual reviewer verifies functionality, performance impact, and safety controls.
  - Release tagging follows semantic version rules once approvals are complete.

## Troubleshooting & Optimization
- **Slow or noisy suggestions:** Tighten Copilot context with smaller files and explicit comments; disable for large generated files.
- **Flaky tests:** Add timeouts, use deterministic seeds, and improve isolation of external dependencies (mocks/sandboxes).
- **Lint failures:** Run formatters locally and check for mixed line endings or missing type hints.
- **CI timeouts:** Cache dependencies, shard tests, and parallelize lint/test steps.
- **Security false positives:** Suppress with documented justifications and targeted ignore rules; never blanket-disable scanners.

## Maintenance Schedule
- Review this guide quarterly or after major architectural changes.
- Align with current CI workflows, dependency policies, and security standards.
- Archive superseded instructions with changelog notes to keep history auditable.

---

**Goal:** Standardize excellence and strengthen the reliability, performance, and safety of the Trading Bot Swarm ecosystem through disciplined automation and assistant behavior.
