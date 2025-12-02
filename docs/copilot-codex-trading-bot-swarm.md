# GitHub Copilot and Codex Configuration Guide for the Trading Bot Swarm Ecosystem

## Purpose and Scope
- Establish a single, enforceable reference for configuring GitHub Copilot and Codex across the Trading Bot Swarm (TBS) repos.
- Frame Copilot as a disciplined pair programmer that respects security, quality, and reliability controls.
- Cover end-to-end guidance: local setup, behavioral rules, CI/CD integration, release/ tagging, and contributor expectations.

## Configuration Overview
1. **Testing and linting:**
   - All code changes **must** run unit tests and linters locally and in CI before merging.
   - Skip automated test/lint runs only when a change is documentation-only.
2. **Code style:**
   - Prefer black/ruff (Python), prettier/eslint (JS/TS), and isort for imports.
   - Enforce typing (e.g., mypy/pyright) for services and shared libraries.
3. **Async patterns:**
   - Use async/await with structured concurrency; avoid fire-and-forget tasks unless guarded.
   - Propagate cancellation tokens/timeouts and wrap I/O with retries and circuit breakers where applicable.
4. **Security defaults:**
   - Never hardcode secrets; use env vars + secret managers. Mask secrets in logs.
   - Enforce least-privilege IAM, signed commits/tags, and supply chain scanning.
5. **Logging and observability:**
   - Standardize structured logging (JSON preferred), request IDs, and correlation IDs.
   - Emit metrics (latency, error rates, retries) and traces for async workflows.
6. **CI/CD integration:**
   - Pre-merge quality gates: lint, test, type-check, security scan.
   - Release gates: semantic-release with automated changelog + signed tags.
7. **Version control:**
   - Conventional commit messages; branch protection requiring status checks.
   - PR templates that demand test evidence and risk notes.

## Custom Instruction Behavior for Copilot and Codex
- Treat Copilot/Codex as rule-driven copilots, not freeform generators.
- Examples of required behaviors:
  - Favor small, reviewable diffs with tests.
  - Default to secure patterns (parameterized queries, input validation, least privilege).
  - Prefer idempotent operations for automation and infra code.
  - Decline to suggest secrets, credentials, or unsafe workarounds.
  - Surface TODOs as explicit backlog items rather than leaving hidden assumptions.

### Conceptual YAML for Custom Instructions
```yaml
copilot_codex:
  role: "disciplined pair programmer"
  objectives:
    - enforce_secure_defaults
    - preserve_code_quality
    - respect_project_style_guides
  rules:
    - "Run or stage tests and linters for any code change; skip only for docs-only diffs."
    - "Use project-standard formatters (black/ruff, isort, prettier/eslint)."
    - "Prefer async/await with explicit timeouts and retries for I/O-bound work."
    - "Never propose secrets, tokens, or unvetted dependencies."
    - "Add logging, metrics, and traces that align with observability conventions."
    - "Recommend small, reviewable PRs with clear context and checklists."
  prompts:
    - "Ask for missing requirements before generating large changes."
    - "Offer test stubs and fixtures alongside new code."
  non_goals:
    - "No generation of legal, licensing, or vendor-locked secrets."
    - "No bypassing CI/CD or branch protections."
```

## Workflow: Lint and Test Automation
**Trigger conditions:**
- `pull_request` on main branches (e.g., `main`, `develop`, release branches).
- `push` to protected branches to guard against bypasses.

**Quality gate job (example):**
```yaml
name: lint-and-test
on:
  pull_request:
    branches: [main, develop, "release/*"]
    paths-ignore:
      - "docs/**"
      - "**/*.md"
  push:
    branches: [main, develop, "release/*"]
    paths-ignore:
      - "docs/**"
      - "**/*.md"
jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          black --check .
      - name: Type check
        run: mypy .
      - name: Test
        run: pytest --maxfail=1 --disable-warnings -q
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          fail_ci_if_error: true
```

## Best Practice Workflows
### Semantic Release and Version Tagging
```yaml
name: semantic-release
on:
  workflow_dispatch:
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
          node-version: '20'
      - name: Install
        run: npm ci
      - name: Lint & Test (gate)
        run: npm test -- --runInBand
      - name: Semantic release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

### Security and Dependency Scanning
```yaml
name: security-scan
on:
  pull_request:
  schedule:
    - cron: '0 3 * * *'
jobs:
  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency audit
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          pip install safety bandit
          safety check --full-report
          bandit -r . -ll
      - name: Trivy file scan
        uses: aquasecurity/trivy-action@0.20.0
        with:
          scan-type: fs
          exit-code: '1'
          ignore-unfixed: true
  container:
    runs-on: ubuntu-latest
    needs: deps
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t tbs-app:ci .
      - name: Trivy image scan
        uses: aquasecurity/trivy-action@0.20.0
        with:
          image-ref: tbs-app:ci
          exit-code: '1'
          ignore-unfixed: true
```

## Contributor Guidelines
- **Proposing changes:** open an issue or draft PR describing scope, risks, test plan, and rollback.
- **Review criteria:** correctness, security posture, tests/coverage, performance impact, observability, and adherence to style guides.
- **Validation:** CI must pass; releases require green pipelines plus manual approval for high-risk changes.
- **Docs:** documentation-only changes skip CI quality gates but must keep instructions current.

## Troubleshooting and Optimization
- **Flaky tests:** rerun in isolation, add timeouts, and use deterministic seeds; mark quarantined tests with follow-up issues.
- **Slow pipelines:** enable caching (pip/pytest caches, Docker layer caching), parallelize independent jobs, and fail fast on lint errors.
- **Permission issues:** verify `GITHUB_TOKEN` scopes and required secrets; prefer OpenID Connect for cloud auth.
- **Noise in Copilot/Codex suggestions:** refine prompts with accepted rules, reduce context size, and pin to project snippets.
- **Dependency conflicts:** use lockfiles, run vulnerability audits, and prefer minimal, vetted dependencies.

## Maintenance Schedule
- **Quarterly** review of this guide for alignment with current CI pipelines, security baselines, and language/tooling versions.
- **Post-incident** updates when RCAs identify new safeguards or process changes.
- **Pre-release** checkpoints to ensure instructions match release tooling and branch protections.

## Closing Note
Standardizing Copilot and Codex behavior, automation workflows, and review criteria strengthens the reliability, performance, and safety of the Trading Bot Swarm ecosystem. Apply these practices to uphold consistent excellence across contributors and services.
