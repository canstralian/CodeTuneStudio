# AGENTS.md

## Environment
- Runtime is CPU-only. Never introduce unconditional CUDA usage.
- If local GPU support is needed, guard it explicitly with an environment check such as `CODEX_ENV`.
- Do not install or upgrade packages at runtime. Update setup scripts or dependency manifests instead.
- External network access is restricted. Follow `codex/templates/INTERNET_ACCESS_POLICY.md`.

## Repository contract
- Preserve compatibility with both PostgreSQL and SQLite fallback.
- Plugin tools must preserve the `AgentTool` contract and the discovery flow in `utils/plugins/base.py` and `utils/plugins/registry.py`.
- Do not introduce unconditional `model.to("cuda")`.
- Prefer narrow, local edits over broad refactors unless the task explicitly requires larger changes.

## Validation
- Prefer targeted tests before full-suite runs unless the change is broad.
- If Python files changed, run the smallest relevant lint and test commands before declaring success.
- State what was validated and what was not.

## Commands the agent should prefer
- Run app: `streamlit run app.py`
- Tests: `pytest`
- Coverage: `pytest --cov=. --cov-report=term-missing`
- CI-critical lint: `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
- Ruff lint: `ruff check .`
- Ruff format: `ruff format .`
- DB health: `python db_check.py`
- Plugin discovery check: `python -c "from utils.plugins.registry import PluginRegistry; r = PluginRegistry(); r.discover_tools('plugins'); print([t.metadata.name for t in r.list_tools()])"`

## Architecture references
- Read `docs/architecture.md` for system structure and invariants.
- Read `docs/runtime.md` for environment-specific behavior if present.

## Task guidance
- For bugfixes, reproduce first if practical, then fix with minimal surface area and add regression coverage.
- For database issues, prefer non-destructive inspection before suggesting resets.
- For new features, match local patterns before introducing new abstractions.