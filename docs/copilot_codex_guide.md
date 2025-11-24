# GitHub Copilot & Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
- Establish consistent AI-assisted development practices across all Trading Bot Swarm services.
- Position Copilot (and Codex-based agents) as disciplined pair programmers that **never bypass quality, security, or safety rules**.
- Standardize logging, observability, CI/CD, and release hygiene so changes are trustworthy and auditable.

## Configuration Overview
1. **Testing & Linting**
   - Run unit tests and integration smoke tests on every change set.
   - Enforce linting (Python: `ruff`, `flake8`, or `black` formatting; JS/TS: `eslint`, `prettier`).
   - Block merges on failed tests/linters; allow doc-only changes to skip heavy suites.
2. **Code Style**
   - Prefer explicit typing, small pure functions, and immutable defaults.
   - Avoid hidden side effects; keep imports deterministic (no try/except around imports).
3. **Async Patterns**
   - Use `asyncio` with cancellation-safe cleanup; prefer `async with`/`async for`.
   - Instrument background tasks with structured logging and timeouts.
4. **Security Defaults**
   - Fail closed: parameterize credentials, prohibit plaintext secrets in code or logs.
   - Enforce dependency pinning and vulnerability scanning before release.
5. **Logging & Observability**
   - Emit timestamped JSON logs containing `request_id`, `service`, and `severity`.
   - Propagate request IDs across HTTP and task queues; export metrics to the shared observability stack (OpenTelemetry/Prometheus).
6. **CI/CD Integration**
   - Pre-merge gates: lint, type-check, tests, security scans, and changelog/semantic commit validation.
   - Post-merge: artifact build, SBOM generation, release drafting, and deployment to staging.
7. **Version Control**
   - Use conventional commits; each PR references a ticket/issue.
   - Keep feature branches rebased; avoid force-pushing to shared branches.

## Custom Instruction Behavior (Copilot & Codex)
- **General Rules**
  - Respect existing architecture and patterns before generating code.
  - Prefer minimal diffs that maximize clarity and testability.
  - Always suggest tests and observability hooks when proposing changes.
- **Security & Privacy**
  - Strip secrets from prompts; avoid generating credentials or private URLs.
  - Recommend least-privilege IAM roles and encrypted secrets management.
- **Testing Discipline**
  - For code changes, require running unit tests and linters; documentation-only edits may skip heavy checks.
  - Surface fast-fail advice (e.g., `pytest -k <scope>`) for large suites.
- **Example Copilot/Codex Custom Instructions (conceptual YAML)**
  ```yaml
  copilot:
    role: "Pair programmer with strict safety and quality enforcement"
    rules:
      - "Follow project logging/observability standards; emit JSON logs with request_id"
      - "Default to typed, side-effect-free functions; avoid broad except"
      - "For any code change, propose tests and run lint+test unless docs-only"
      - "Never suggest storing secrets in code or logs"
  codex:
    role: "Automation agent for refactors and CI tooling"
    rules:
      - "Preserve public APIs and compatibility tests"
      - "Use conventional commits and semantic version hints"
      - "Add metrics/logging hooks when introducing new workflows"
  ```

## GitHub Workflow Example (Lint & Test Automation)
- **Triggers**: `pull_request` (opened, synchronize, reopened), `push` to `main`.
- **Quality Gate Job** (Python example):
  ```yaml
  name: quality-gate
  on:
    pull_request:
      branches: ["main"]
    push:
      branches: ["main"]
  jobs:
    lint-test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.11'
        - name: Install deps
          run: pip install -r requirements.txt
        - name: Lint
          run: ruff check .
        - name: Type check
          run: pyright
        - name: Tests
          run: pytest --maxfail=1 --disable-warnings -q
  ```

## Semantic Release & Version Tagging
- Adopt semantic versioning (`MAJOR.MINOR.PATCH`).
- Enforce conventional commit prefixes (`feat:`, `fix:`, `chore:`, `docs:`).
- Release workflow (example):
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
        - name: Use Node.js
          uses: actions/setup-node@v4
          with:
            node-version: '20'
        - name: Install
          run: npm ci
        - name: Semantic Release
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          run: npx semantic-release
  ```
- Tag releases automatically; publish changelogs and artifacts; gate production deploys on tagged builds.

## Security & Dependency Scanning
- Run SAST/secret scanning on PRs (e.g., `gitleaks`, `trivy config`).
- Run dependency audits (`pip-audit`, `npm audit`, `trivy fs`).
- Example combined job:
  ```yaml
  name: security-scan
  on:
    pull_request:
      branches: ["main"]
  jobs:
    sast-and-deps:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Secret scan
          uses: gitleaks/gitleaks-action@v2
        - name: Python deps audit
          run: pip install pip-audit && pip-audit
        - name: Container scan (optional)
          run: |
            docker build -t trading-bot-swarm .
            trivy image --exit-code 1 trading-bot-swarm
  ```

## Contributor Guidelines
- **Proposing Changes**
  - Open an issue/PR with scope, risks, and rollout steps.
  - Include test plan, observability notes, and migration/backfill details.
- **Review Criteria**
  - Code clarity, typing, and adherence to logging/metrics standards.
  - Passing tests/linters and security scans; no secrets in diffs or logs.
  - Backward compatibility and documented edge cases.
- **Validation Process**
  - Reviewer confirms request IDs and JSON logs appear in preview environments.
  - Merge only after CI green and release notes updated (if user-facing change).

## Troubleshooting & Optimization
- **Flaky tests**: quarantine and add deterministic seeding plus logging contexts.
- **CI timeouts**: shard tests, cache dependencies, and trim integration scope.
- **Copilot noise**: tighten context windows and restate rules in file headers.
- **Logging overload**: drop verbosity for hot paths; rely on structured fields instead of verbose strings.

## Maintenance Schedule
- Quarterly review of this guide alongside dependency baseline and security policies.
- Update logging/observability sections whenever platform standards change.
- Revalidate CI workflows after major runtime/toolchain upgrades.

---
**Goal:** Standardize excellence—strengthening reliability, performance, and safety across the Trading Bot Swarm ecosystem.
