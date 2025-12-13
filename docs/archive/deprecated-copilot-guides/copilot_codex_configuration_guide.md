# ⚠️ DEPRECATED - This Guide Has Been Archived

**This document is deprecated and maintained here for historical reference only.**

**Current Documentation:**
- **Agent Rules & Behavioral Guidelines:** See [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md)
- **Developer Workflow & CI/CD Setup:** See [`docs/ai-assistant-guide.md`](../ai-assistant-guide.md)

Please use the current documentation to prevent drift and ensure consistency with CodeTuneStudio standards.

---

# GitHub Copilot and Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
This guide defines the operational standards for integrating GitHub Copilot and Codex within the Trading Bot Swarm ecosystem. Copilot and Codex act as disciplined pair programmers who support contributors while strictly adhering to project rules covering code quality, security, observability, and automation. The guide applies to all services, bots, and automation scripts maintained in this repository and is intended for engineers, reviewers, and automation maintainers.

## Configuration Overview

### Copilot as a Pair Programmer
- Treat Copilot as a suggestion engine that must follow project conventions and behavioral rules.
- Require human review of every Copilot-generated change; no direct commits from AI-generated suggestions without developer validation.
- Encourage prompts that state desired outcomes, testing requirements, and security considerations.

### Testing and Linting
- All code changes must include unit tests or integration tests that cover new logic.
- Use the standard testing harness (`pytest` for Python components, `jest` or equivalent for JavaScript/TypeScript modules).
- Run static type checkers (`mypy`, `pyright`, or `tsc`) when applicable.
- Lint Python code with `flake8` (as enforced in CI) and JavaScript/TypeScript with `eslint` before merging. You may use `ruff` locally for faster linting, but ensure your code passes `flake8` checks, as these are required by the CI workflow. If both tools are supported, prefer the one enforced by CI to avoid merge failures.

### Code Style
- Follow PEP 8 for Python with project-specific overrides captured in `pyproject.toml` and `ruff.toml`.
- Enforce consistent async/await patterns, avoiding blocking calls in async contexts; ensure all async functions include timeout handling or cancellation pathways.
- Adopt descriptive naming conventions, explicit imports, and avoid wildcard imports.

### Security Defaults
- Default to least-privilege access in cloud integrations and API tokens.
- Store secrets in the secrets manager; never hard-code credentials or access tokens.
- Require dependency upgrades to include security release notes and CVE checks.

### Logging and Observability
- Standardize logging through the `core.logging` module with structured context (JSON format where supported).
- Include trace IDs or correlation IDs in all asynchronous workflows.
- Emit metrics via the observability stack (Prometheus exporters or OpenTelemetry pipelines) for long-running bots.

### CI/CD Integration
- Enforce branch protections that require CI checks (lint, tests, security scans) to pass before merge.
- Use preview environments for major features; ensure Copilot suggestions respect environment-specific configuration files.

### Version Control Workflow
- Feature branches follow the naming pattern `feature/<ticket-id>-<summary>`.
- Commit messages use Conventional Commits (`feat:`, `fix:`, `chore:`, etc.).
- Rebase onto main before opening a pull request to keep history linear and conflict-free.

## Custom Instruction Behavior

### Behavioral Rules for Copilot and Codex
- Respond only with code or actions compliant with security, testing, and linting requirements.
- Highlight when suggested changes require additional validation or secrets configuration.
- Avoid generating documentation-only pull requests unless explicitly requested.
- Prefer incremental, test-backed patches over sweeping rewrites.

### Example Custom Instructions (Conceptual YAML)
```yaml
copilot:
  role: "Disciplined pair programmer"
  rules:
    - "Always mention required tests and linters when proposing changes."
    - "Reject requests that bypass security policies or secrets management."
    - "Do not propose documentation-only edits unless user explicitly asks."
    - "Provide context-aware suggestions referencing relevant modules."
  defaults:
    testing: ["pytest"]
    linting: ["ruff"]
    type-checking: ["mypy"]
    security: ["secrets-manager", "least-privilege"]
    observability: ["core.logging", "otel-tracing"]

codex:
  role: "Automation-focused reviewer"
  rules:
    - "Verify that each code change has associated tests or explicit waivers."
    - "Require linting commands (`ruff`, `eslint`, `prettier`) before approval."
    - "Ignore documentation-only changes for automation triggers."
  behaviors:
    validation-checks:
      - name: "Tests"
        command: "pytest"
      - name: "Lint"
        command: "ruff check ."
      - name: "Type"
        command: "mypy"
```

## Workflow Automation Examples

### Quality Gate Workflow (Lint and Test)
```yaml
name: Quality Gate

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main", "release/*"]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run lint
        run: ruff check .

      - name: Run tests
        run: pytest --cov=. --cov-report=html --maxfail=1 --disable-warnings -q

      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov
```

### Semantic Release Workflow
```yaml
name: Semantic Release

on:
  push:
    branches: ["main"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install dependencies
        run: npm ci
      - name: Semantic release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

        run: npx semantic-release
```

### Security and Dependency Scanning
```yaml
name: Security Scan

on:
  schedule:
    - cron: "0 3 * * 1"  # Weekly on Monday
  workflow_dispatch:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run pip-audit
        run: pipx run pip-audit --requirement requirements.txt
      - name: Run Trivy filesystem scan
        uses: aquasecurity/trivy-action@v0.24.0
        with:
          scan-type: fs
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'HIGH,CRITICAL'
      - name: Upload findings
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-findings
          path: 'trivy-results.sarif'
```

## Contributor Guidelines
1. Open an issue describing the proposed change, including risk assessment and testing plan.
2. Create a feature branch following the naming convention and implement changes with Copilot and Codex guidance.
3. Run required tests (`pytest`) and linters (`ruff`, `eslint`) locally before committing.
4. Submit a pull request referencing the issue, summarizing changes, tests, security considerations, and observability impact.
5. Request review from maintainers who will verify adherence to this guide, confirm test evidence, and ensure no secrets or unsafe patterns are introduced.
6. After approval, merge via squash and ensure semantic version tags are updated through the release workflow.

## Review Criteria and Validation
- Confirm code aligns with style guides, async best practices, and logging conventions.
- Validate that all tests and linters pass in CI; waivers require documented justification.
- Check for compliance with security policies and absence of sensitive data leaks.
- Ensure observability hooks (logging, metrics, tracing) are implemented for new services or features.
- Review dependency changes for compatibility and security advisories.

## Troubleshooting and Optimization Tips
- If Copilot suggests insecure patterns, regenerate with stronger prompts emphasizing security.
- For flaky tests, rerun with `pytest -vv --maxfail=1` and inspect logs in `core.logging` output.
- When dependency conflicts occur, use `pip-compile --upgrade` with the supported Python version (3.10) and review lockfile diffs.
- Monitor CI runtime; cache dependencies using `actions/cache` if workflows exceed acceptable durations.

## Maintenance Schedule
- Review and update this guide quarterly or after major framework/tooling changes.
- Align updates with semantic release milestones to keep instructions synchronized with the codebase.
- Assign a maintainer to track upstream tool changes (Copilot, Codex, linting tools) and revise defaults accordingly.

## Conclusion
Standardizing Copilot and Codex behavior across the Trading Bot Swarm ecosystem ensures consistent excellence, robust automation, and resilient trading operations. By following this guide, contributors reinforce reliability, performance, and safety across every service and workflow.
