# GitHub Copilot & Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
This guide standardizes how GitHub Copilot and Codex operate across the Trading Bot Swarm ecosystem. Copilot acts as a disciplined pair programmer that prioritizes reliability, security, and consistency. The instructions ensure generated code meets the project's expectations for testing, linting, observability, and CI/CD integration while protecting credentials and data.

## Configuration Overview
- **Testing and Linting**: Every code change must run unit tests and linters. Documentation-only changes can skip automated execution but must state why. Prefer `pytest -q` and fast linters (e.g., `ruff`, `flake8`).
- **Code Style**: Adhere to PEP 8, project-specific formatting, and typed interfaces. Keep functions small, pure where possible, and favor dependency injection for testability.
- **Async Patterns**: Use `async`/`await` for IO-bound workflows. Avoid blocking calls in async contexts; use `asyncio` timeouts and cancellation-safe cleanup.
- **Security Defaults**: Never hard-code secrets. Use environment variables or secret managers, enable least-privilege tokens, and validate external inputs. Prefer safe defaults (closed ports, deny-by-default network policies, sanitized logs).
- **Logging & Observability**: Emit structured logs with correlation IDs. Include key state transitions, error context, and metrics hooks (latency, failure counts). Prefer OpenTelemetry-compatible instrumentation.
- **CI/CD Integration**: All merges should pass lint, tests, and security scans. Block deployments on failing quality gates. Artifacts should be reproducible and traceable to commits.
- **Version Control**: Use feature branches, small atomic commits, and semantic PR titles. Reference issue IDs where possible and keep history clean (rebase over merge commits within PR branches).

## Custom Instruction Behavior
Codex and Copilot must follow strict behavior rules when assisting contributors:
- Favor clarity over brevity in suggestions; always align with project patterns.
- Refuse to generate code that bypasses tests, hides errors, or disables security checks.
- Add contextual comments only when they improve comprehension (avoid noise).
- Prefer explicit dependencies and pinned versions; avoid transitive surprises.
- For documentation-only changes, omit test/lint prompts but remind contributors to keep references accurate.

### Example Rule Set (YAML Concept)
```yaml
assistant-behavior:
  role: "pair-programmer"
  safety:
    forbid-hardcoded-secrets: true
    disallow-insecure-tempfiles: true
    require-input-validation: true
  quality:
    enforce-type-hints: true
    require-tests-and-linters: true
    reject-dead-code: true
  async:
    avoid-blocking-calls: true
    mandate-timeouts: true
  observability:
    structured-logging: true
    add-correlation-ids: true
  documentation:
    skip-tests-for-doc-only: true
    remind-to-note-skip-reason: true
```

## Workflow Example: Lint & Test Automation
Trigger on pull requests to `main` and `develop`, and on manual dispatch:
```yaml
name: Quality Gate

on:
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run linters
        run: |
          ruff check .
          flake8
      - name: Run tests
        run: pytest -q
```

## Best Practices: Releases and Scanning
- **Semantic Release & Version Tagging**: Automate changelog generation and tagging after main branch merges.
```yaml
name: Semantic Release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: "lts/*"
      - run: npm ci
      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```
- **Security & Dependency Scanning**: Run regularly and on pull requests.
```yaml
name: Security Scan
on:
  schedule:
    - cron: "0 3 * * *"
  pull_request:

jobs:
  dependency-review:
    permissions:
      contents: read
      pull-requests: write
      security-events: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
  sast-and-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy security scan
        uses: aquasecurity/trivy-action@0.24.0
        with:
          scan-type: fs
          format: table
          severity: HIGH,CRITICAL
```

## Contributor Guidelines
- **Proposing Changes**: Open an issue outlining scope, risks, and testing impact. Use feature branches and keep diffs focused.
- **Review Criteria**: Changes must include tests (or justification), follow style guides, and maintain observability hooks. Security-sensitive updates require explicit threat modeling notes.
- **Validation Process**: PRs must pass the Quality Gate workflow. Maintainers verify change logs, dependency updates, and deployment notes before merge.

## Troubleshooting & Optimization
- **Copilot Noise**: Reduce suggestion volume by scoping prompts (e.g., comment blocks describing desired signature) and enforcing rule reminders.
- **Async Pitfalls**: Replace blocking libraries with async equivalents; use `asyncio.wait_for` to bound latency.
- **Flaky Tests**: Add deterministic seeds, mock external services, and improve fixture teardown to avoid resource leaks.
- **Dependency Conflicts**: Pin upper/lower bounds, run `pip check`, and regenerate locks when major versions shift.

## Maintenance Schedule
- **Quarterly**: Review instructions for new security policies, linter upgrades, and CI changes. Refresh screenshots or examples as needed.
- **Release Cycles**: Align guide updates with semantic release milestones to keep workflows current.
- **Incident Retrofits**: After outages or security events, append lessons learned and mitigation steps.

## Closing Note
Standardizing Copilot and Codex behavior reinforces reliability, performance, and safety across the trading ecosystem. Apply these guidelines to keep automation trustworthy and resilient.
