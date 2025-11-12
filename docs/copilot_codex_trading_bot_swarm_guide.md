# Trading Bot Swarm Copilot & Codex Configuration Guide

## Purpose and Scope

This guide defines how to configure GitHub Copilot and Codex inside the Trading Bot Swarm ecosystem. It aligns AI-assisted development with our security-first automation standards, codifies guardrails for pair-programming interactions, and sets expectations for verification before code merges. Copilot is treated as a strictly managed collaborator that suggests code, while human maintainers remain accountable for correctness, compliance, and safety.

## Configuration Overview

### Behavioral Principles for AI Pair Programmers

1. Copilot must never auto-commit or push code; suggestions require human review.
2. Generated code must respect project licensing, security defaults, and dependency policies.
3. Suggestions must preserve existing abstractions, naming, and architectural layering.
4. Copilot is configured to default to safe, idempotent operations, minimizing side effects.

### Testing and Linting

* All code contributions must include relevant unit, integration, and property tests when functionality changes.
* Linters (e.g., `ruff`, `flake8`, `eslint`) and formatters (`black`, `prettier`) run locally before commits and again in CI.
* Tests failing locally block pull requests; only documentation-only PRs may skip automated tests.

### Code Style and Patterns

* Python: `black` formatting, `ruff` linting, type annotations with `mypy` or `pyright` where applicable.
* JavaScript/TypeScript: `prettier` formatting, `eslint` with project rules, and strict TypeScript configuration.
* Async patterns favor `asyncio` with explicit timeouts and cancellation handling.
* Prefer dependency injection over global state to support deterministic testing.

### Security Defaults

* Enforce least-privilege access to secrets; use short-lived credentials and secret scanners.
* Treat AI suggestions as untrusted: verify input validation, output encoding, and error handling.
* Require threat modeling for new external integrations and specify secure defaults (e.g., TLS v1.2+).

### Logging, Observability, and Metrics

* Copilot-generated code must respect structured logging standards (JSON logs with context).
* Ensure metrics and tracing instrumentation propagate trace IDs and avoid leaking PII.
* Instrument new services with OpenTelemetry where available.

### CI/CD Integration

* CI enforces linting, testing, security scans, and dependency freshness.
* CD pipelines require manual approval when AI-assisted changes touch production services.
* Deployment manifests reference immutable builds; rollback procedures are documented.

### Version Control Practices

* Require signed commits from maintainers.
* Branch naming convention: `feature/<scope>`, `bugfix/<scope>`, `chore/<scope>`.
* Pull requests must include change rationale, testing evidence, and security considerations.

## Custom Instruction Behavior

### Example Rules for Codex and Copilot

1. Respect project coding standards for languages, frameworks, and test coverage.
2. Prioritize deterministic, testable code; avoid network calls in unit tests.
3. Flag potential security issues (e.g., SQL injection, hardcoded secrets).
4. Provide inline comments explaining non-obvious logic or safeguards.
5. Suggest refactoring opportunities but avoid large rewrites in a single change.

### Conceptual YAML for Custom Instructions

```yaml
copilot:
  role: "Pair programmer with strict review gate"
  behaviors:
    - "Never push or commit changes"
    - "Follow project code style and lint rules"
    - "Surface test additions when functionality changes"
    - "Highlight security concerns and compliance requirements"
    - "Defer to human decisions on architectural changes"
  prompts:
    - "Before suggesting code, summarize assumptions"
    - "After suggestions, list recommended tests"

codex:
  role: "Automation assistant for scripted tasks"
  behaviors:
    - "Use idempotent scripts"
    - "Guard secrets and redact sensitive output"
    - "Integrate logging with structured JSON"
    - "Emit lint/test commands prior to concluding output"
  prompts:
    - "Return patches with minimal scope"
    - "Cite files and commands modified"
```

### Verification Requirements

* Every Copilot suggestion incorporated into a PR must undergo manual review and follow-up testing.
* Automated lint/test runs are mandatory for code changes; documentation-only changes may skip but must note exemption in the PR description.
* Security scanners run nightly and on-demand for high-risk branches.

## GitHub Workflow: Lint and Test Automation

Trigger the workflow on pull requests and pushes to protected branches:

```yaml
name: lint-and-test

on:
  push:
    branches: ["main", "release/*"]
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          black --check .
      - name: Run tests
        run: pytest --maxfail=1 --disable-warnings -q
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          fail_ci_if_error: true
```

## Semantic Release and Version Tagging

### Workflow Overview

* Adopt conventional commits for automated changelog generation.
* Use semantic-release to calculate the next version and publish tags.
* Release pipeline triggers on merges to `main` and manual release branches.

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
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npx semantic-release
```

## Security and Dependency Scanning

### Scheduled and On-Demand Scans

* Enable Dependabot alerts and automated dependency update PRs.
* Run SAST, secret scanning, and SBOM generation on each PR.

```yaml
name: security-scan

on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
      - name: Run Snyk SAST
        uses: snyk/actions/python@v0.4.0
        with:
          command: test
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      - name: Dependency audit
        run: pip install pip-audit && pip-audit
      - name: Secret scan
        uses: trufflesecurity/trufflehog@v3
```

## Contributor Guidelines

1. **Proposal Stage:** Open an issue describing motivation, scope, risk classification, and testing strategy.
2. **Implementation:** Create a feature branch, run lint/tests locally, document assumptions, and capture Copilot involvement.
3. **Review:** Reviewers verify architectural alignment, security posture, test coverage, and adherence to this guide.
4. **Validation:** Merge only after CI passes, security scans are clean, and at least two approvals for high-risk changes.

## Troubleshooting and Optimization

* **Copilot Quality Issues:** Regenerate suggestions with stricter prompts, provide context files, and prefer smaller diff requests.
* **Test Failures:** Re-run locally with verbose logging; ensure deterministic fixtures and isolate network calls.
* **Lint Errors:** Run formatters automatically on save and configure IDE linting integrations.
* **Security Alerts:** Validate false positives, patch vulnerabilities promptly, and document compensating controls.

## Maintenance Schedule

* Quarterly review of tooling versions, workflows, and instructions.
* Post-incident updates to include new security or reliability lessons.
* Annual audit aligning the guide with regulatory changes and ecosystem standards.

## Closing Note

By standardizing excellence across Copilot and Codex workflows, we reinforce the Trading Bot Swarm’s reliability, performance, and safety—ensuring every automated decision upholds our commitment to secure, high-quality trading systems.

