# GitHub Copilot and Codex Configuration Guide for Trading Bot Swarm

## Purpose and Scope
- Establish a unified configuration for GitHub Copilot and Codex across the Trading Bot Swarm ecosystem.
- Treat Copilot as a disciplined pair programmer that suggests code only when it aligns with project policies.
- Define behavioral rules, automation expectations, and guardrails that preserve reliability, performance, and safety in trading workflows.

## Configuration Overview
### Testing Strategy
- Run the full automated test suite (`pytest`, integration tests, and smoke tests) for any change affecting executable code.
- Use targeted test selection for scoped updates, but always execute a final full run before merging to main.
- Require green test runs before approving pull requests or triggering deployments.

### Linting and Static Analysis
- Enforce `ruff` for Python, `eslint` for JavaScript/TypeScript, and `shellcheck` for Bash utilities.
- Integrate type checking (`mypy`, `pyright`, `tsc`) into the CI gate.
- Block commits that fail linting or introduce new warnings.

### Code Style and Patterns
- Follow the project `pyproject.toml` formatter settings (Black-compatible 88-column limit, import sorting via `ruff`).
- Prefer dependency injection over singletons; document side effects explicitly.
- Design asynchronous flows using `asyncio` tasks, `anyio`, or project-approved concurrency helpers.
- Avoid blocking calls inside async contexts; wrap external I/O in asynchronous adapters when available.

### Security Defaults
- Deny dangerous suggestions (e.g., plaintext secrets, shell eval, dynamic SQL) from Copilot/Codex.
- Default to least-privilege credentials and enforce secret scanning pre-commit hooks.
- Require parameterized queries, prepared statements, and upstream validation for any user input.

### Logging and Observability
- Emit structured logs (JSON) with correlation IDs using the shared logging utility.
- Record audit events for model training runs, experiment configuration changes, and user access changes.
- Export Prometheus metrics for latency, order volume, and error rates; surface alerts in Grafana.

### CI/CD Integration
- Treat `main` as production-ready; protect with required reviews and status checks.
- Use staging environments for canary deployments; promote automatically when canary metrics remain healthy for 30 minutes.
- Automate rollbacks with feature flags and deployment health monitors.

### Version Control Workflow
- Adopt trunk-based development with short-lived branches.
- Prefix branches with the workstream (`feat/`, `fix/`, `chore/`, `sec/`).
- Squash merge feature branches after successful review and quality gates.

## Custom Instruction Behavior for Copilot and Codex
### Behavioral Principles
- Suggest only code that compiles, passes linters, and adheres to security controls.
- Never auto-commit; all changes require human validation and tests.
- Prefer referencing existing project abstractions before introducing new utilities.
- Highlight missing tests whenever Copilot proposes functionality changes.

### Example Rule Set
1. Respect domain-driven boundaries (`core/`, `plugins/`, `components/`, `utils/`).
2. Annotate all public functions with type hints and docstrings.
3. Prompt for test updates (`tests/` mirror path) for every behavior change.
4. Avoid modifying documentation-only files when responding to code refactor requests.

### Conceptual YAML Custom Instructions
```yaml
copilot:
  role: "Pair programmer with strict compliance focus"
  must_do:
    - "Run pytest and linters after editing executable code"
    - "Refuse to alter documentation-only changes unless explicitly asked"
    - "Call out missing security considerations in suggestions"
    - "Use established logging helpers for observability"
  must_not_do:
    - "Introduce network bindings outside approved ports"
    - "Commit code without human review"
    - "Generate secrets or placeholder credentials"
  code_style:
    python: "black, ruff, mypy"
    javascript: "prettier, eslint, typescript"
    shell: "shellcheck"

codex:
  role: "Automation orchestrator for Trading Bot Swarm"
  execution_policy:
    - "Execute tests via tox or uv for Python packages"
    - "Trigger async-safe patterns for any bot orchestration"
    - "Skip workflow triggers for markdown-only changes"
  guardrails:
    - "Escalate if requested action weakens security posture"
    - "Refuse to run unsigned third-party scripts"
  reporting:
    - "Post execution summaries to Observability channel"
```

## GitHub Workflow: Lint and Test Automation
- **Trigger Conditions:** `pull_request`, `push` to `main`, and nightly `schedule`.
- **Quality Gate Job:**
  1. Checkout repository with full history for semantic analysis.
  2. Set up Python `3.11` and Node `20`.
  3. Install dependencies via `uv sync` (Python) and `pnpm install --frozen-lockfile` (JS).
  4. Run `ruff check`, `black --check`, `mypy`, `pytest -q`, `eslint`, and integration smoke tests.
  5. Upload coverage report to Codecov and lint artifacts for audit.

```yaml
name: lint-and-test

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 3 * * *"

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install Python dependencies
        run: uv sync
      - name: Install JS dependencies
        run: pnpm install --frozen-lockfile
      - name: Static analysis
        run: |
          ruff check .
          black --check .
          mypy .
          pnpm lint
      - name: Run tests
        run: |
          pytest -q
          pnpm test
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

## Semantic Release and Version Tagging Workflow
- Automate version bumps using commit conventions (`feat`, `fix`, `perf`, `sec`).
- Publish tags only after quality gates pass and staging verification succeeds.
- Generate release notes with categorized changes and dependency diffs.

```yaml
name: semantic-release

on:
  push:
    branches: [main]

jobs:
  release:
    if: github.repository == 'TradingBotSwarm/platform'
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
      - run: pnpm install --frozen-lockfile
      - name: Semantic release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: pnpm semantic-release
```

## Security and Dependency Scanning Workflow
- Run on pull requests and weekly schedules.
- Check Python dependencies with `pip-audit`, JavaScript with `pnpm audit`, and container images with `trivy`.
- Fail builds on high or critical vulnerabilities.

```yaml
name: security-scan

on:
  pull_request:
  schedule:
    - cron: "0 1 * * 1"

jobs:
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Python audit
        run: pipx run pip-audit
      - name: Node audit
        run: pnpm audit --audit-level=high
      - name: Container scan
        uses: aquasecurity/trivy-action@0.24.0
        with:
          scan-type: filesystem
          ignore-unfixed: true
          severity: HIGH,CRITICAL
```

## Contributor Guidelines
- **Proposing Changes:** Open an issue describing scope, risk impact, and rollout plan. Branch from `main` using the prescribed prefix.
- **Review Criteria:** Ensure code follows style guides, includes tests, passes CI, and documents operational impacts in the changelog.
- **Validation Process:**
  1. Developer runs local linting and tests.
  2. Reviewer verifies test artifacts, security posture, and observability coverage.
  3. Merge after two approvals and all status checks succeed.

## Troubleshooting and Optimization Tips
- If Copilot suggestions drift, reset context by summarizing current task and reiterating guardrails.
- For flaky tests, annotate with `@flaky` only after logging an issue and documenting mitigation steps.
- When lint rules conflict, prefer the stricter rule and update shared configs to match.
- Cache dependency installs in CI (`actions/cache`) to reduce runtime, but invalidate on lockfile changes.

## Maintenance Schedule
- Review this guide quarterly alongside dependency updates and architectural changes.
- Sync Copilot/Codex instruction YAML with project configuration repositories after each release train.
- Audit automation workflows biannually for deprecated actions or security advisories.

## Conclusion
Standardizing Copilot and Codex behavior ensures consistent excellence across Trading Bot Swarm. By enforcing rigorous testing, observability, and security workflows, we strengthen the reliability, performance, and safety of the trading ecosystem.
