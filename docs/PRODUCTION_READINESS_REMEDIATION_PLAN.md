# Production Readiness Remediation Plan

This plan translates the repository audit findings into a staged, execution-ready roadmap.

## Baseline

- **Current maturity**: staging-ready
- **Target maturity**: enterprise production-ready
- **Primary constraints**: CPU-only runtime, Streamlit + Flask monolith, plugin contract stability

## Phase 0 (Week 0-1): Immediate Risk Reduction

### 0.1 Legal and metadata alignment
- Align license statements across all project documents and metadata.
- Add CI check that fails when declared license strings diverge from `LICENSE`.

### 0.2 Security guardrails in CI
- Add mandatory dependency vulnerability scan (`pip-audit`) in CI.
- Add secrets scanning (e.g., `gitleaks`) on pull requests.
- Add static security scan (Bandit or Semgrep) with failing threshold for high-severity findings.

### 0.3 Test policy enforcement
- Add coverage floor (70%) in pyproject.toml.
- Fail CI on coverage regression.
- Define baseline markers (`unit`, `integration`, `e2e`, `security`).

## Phase 1 (Week 1-3): Minimum Production Bar

### 1.1 Authentication and authorization
- Introduce authn/authz for all mutating operations.
- Add role model: `admin`, `operator`, `viewer`.
- Protect plugin execution and training actions with least-privilege checks.

### 1.2 Operational observability
- Add structured JSON logging for Streamlit/Flask services.
- Instrument metrics (request latency, error rate, queue depth, training health).
- Add tracing support (OpenTelemetry) for critical flows.
- Publish initial runbook for incident triage.

### 1.3 Persistence and recovery posture
- Define managed PostgreSQL as production default; keep SQLite fallback for dev only.
- Add migration runbook and migration smoke test.
- Document backup cadence and restore validation procedure.

## Phase 2 (Week 3-6): Reliability and Hardening

### 2.1 Testing expansion
- Add integration tests for:
  - database write/read paths
  - plugin discovery lifecycle
  - Flask ↔ Streamlit interaction boundaries
- Add one E2E happy-path workflow: dataset → training config → run → metrics view.

### 2.2 Supply chain security
- Generate SBOM (CycloneDX/SPDX) during CI.
- Add license compliance checks for dependency graph.
- Add container image scanning in build pipeline.

### 2.3 Build reproducibility
- Reconcile dependency declarations (`pyproject.toml` vs `requirements.txt`).
- Introduce lockfile strategy and deterministic install path.
- Pin base image by digest in Dockerfile.

## Phase 3 (Week 6-10): Scale and Enterprise Controls

### 3.1 Deployment maturity
- Add container orchestration artifacts (Kubernetes or Compose for staged environments).
- Add health/readiness/liveness probes and graceful shutdown policies.

### 3.2 Performance and resilience
- Add load tests for concurrent training/session workloads.
- Define SLOs (availability, latency, successful run ratio) and alert thresholds.
- Add chaos/failure drills for DB failover and plugin provider outages.

### 3.3 Governance and compliance
- Introduce change management checklist for production-impacting changes.
- Add incident response playbook, RTO/RPO targets, and postmortem template.

## Acceptance Criteria (Production Readiness Gate)

Release candidates should satisfy all criteria below:

1. Auth enabled and verified for sensitive actions.
2. CI includes lint, unit, integration, security scans, and coverage gates.
3. Coverage meets policy thresholds and does not regress.
4. Database migrations are forward-tested and rollback strategy is documented.
5. Observability stack (logs/metrics/traces) is operational with dashboards.
6. Backup + restore run successfully in a staged environment.
7. SBOM and vulnerability scan artifacts are published per build.
8. Deployment artifacts and operational runbooks are versioned in-repo.

## Suggested Ownership Model

- **Security lead**: CI security scans, threat model, secrets policy
- **Platform lead**: deployment, runtime configuration, observability
- **Application lead**: authn/authz, plugin execution controls, test architecture
- **Release manager**: readiness gates, sign-off, rollback governance

## Recommended first pull requests

1. CI security job (`pip-audit`, secrets scan, SAST)
2. `pytest.ini` with coverage floor + CI enforcement
3. Dependency reconciliation and lockfile introduction
4. Auth middleware skeleton + protected training/plugin endpoints
5. Observability bootstrap (structured logs + metrics endpoint)