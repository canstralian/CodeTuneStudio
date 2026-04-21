# CLAUDE.md

# Environment
- Runtime is CPU-only. Never introduce unconditional CUDA usage.
- If local GPU support is needed, guard it explicitly with `CODEX_ENV`.
- Do not install or upgrade packages at runtime. Update `codex/setup.sh` or repo manifests instead.
- External network access is restricted. Follow `codex/templates/INTERNET_ACCESS_POLICY.md`.

# Commands Claude would not reliably guess
- CI-critical lint: `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
- DB health check: `python db_check.py`
- Plugin discovery check: `python -c "from utils.plugins.registry import PluginRegistry; r = PluginRegistry(); r.discover_tools('plugins'); print([t.metadata.name for t in r.list_tools()])"`

# Project invariants
- Plugin tools must preserve the `AgentTool` contract and discovery flow in `utils/plugins/base.py` and `utils/plugins/registry.py`.
- Database changes must remain compatible with both PostgreSQL and SQLite fallback.
- Prefer targeted tests over full-suite runs unless the change is broad.
- Do not introduce unconditional `model.to("cuda")`.

# Imports
- @docs/architecture.md
- @~/.claude/personal-overrides.md