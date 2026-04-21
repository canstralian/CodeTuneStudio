# Architecture

CodeTuneStudio is a hybrid Streamlit/Flask application for model fine-tuning, experiment tracking, and plugin-based tooling.

## Primary structure

- `app.py` is the main entry point.
- `components/` contains modular Streamlit UI units.
- `utils/` contains database, training, visualization, and orchestration code.
- `plugins/` contains dynamically discovered tools.
- `tests/` contains unit and integration tests.

## Runtime model

- Streamlit provides the interactive UI.
- Flask and SQLAlchemy handle backend and persistence concerns.
- PostgreSQL is preferred when configured.
- SQLite fallback must remain supported.

## Plugin architecture

Plugins are discovered dynamically from `plugins/`.

Required invariants:
- Plugin classes must follow the `AgentTool` contract from `utils/plugins/base.py`.
- Discovery flow in `utils/plugins/registry.py` must remain intact.
- Changes must not silently break registration, metadata, or duplicate-protection behavior.

## Training and inference constraints

- Runtime execution is CPU-only unless explicitly guarded for local environments.
- Training and inference code must not assume CUDA.
- Configuration and experiment tracking behavior should remain stable across changes.

## Change guidance

When modifying this repository:
- Prefer narrow edits over broad refactors.
- Preserve compatibility with both database backends.
- Match existing local patterns before introducing new abstractions.
- Add or update tests when behavior changes.