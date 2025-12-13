# CodeTuneStudio

**AI suggestions are cheap. Validated changes are not.**

CodeTuneStudio is a **Streamlit + Flask** application with a **plugin architecture** for code and workflow tooling. Today it provides an interactive UI for running the app, exploring plugins, configuring workflows, and integrating with LLM-backed analysis (OpenAI/Anthropic plugins). The next MVP step is a validation pipeline that turns “AI output” into “tool-gated evidence”.

---

## What you get today (verifiable in this repo)

### ✅ A working UI-first experience
- A Streamlit UI orchestrated by `core/server.py` (`MLFineTuningApp`).
- A hybrid Flask backend for database operations (SQLAlchemy + Flask-Migrate).
- Modular UI components in `components/`.

### ✅ Extensible plugin system
- Plugins implement `AgentTool` (`utils/plugins/base.py`) and are discovered dynamically (`utils/plugins/registry.py`).
- Plugin implementations live in `plugins/` (including LLM-backed analysis plugins).

### ✅ Optional LLM integrations (when API keys are configured)
- OpenAI plugin(s) use `OPENAI_API_KEY`.
- Anthropic plugin(s) use `ANTHROPIC_API_KEY`.

### ✅ Quality tooling + CI discipline exists
- Pre-commit configuration exists (`.pre-commit-config.yaml`).
- CI workflows exist under `.github/workflows/`.

> This landing page does **not** claim that CodeTuneStudio already generates patches, applies diffs, or validates multiple candidate refactors against your test suite. That is the MVP work described below.

---

## What we’re building next (MVP: Validation Pipeline — in progress)

The MVP validation pipeline is the missing layer between **LLM output** and **mergeable code**:

- **Candidate strategies:** generate 2–3 alternative change strategies (as diffs/patches).
- **Sandboxed execution:** apply each candidate in an isolated workspace.
- **Tool-gated validation:** run repo tooling (pytest + ruff/flake8 + mypy) and capture deterministic results.
- **UI comparison:** present pass/fail + warnings/errors side-by-side in the UI.
- **Export artifact:** export a patch/diff for manual application and review.

This will be implemented to **fail-closed** (no “looks good” without tool evidence).

---

## Who it’s for

**For:**
- Engineers using AI assistants who want **inspectable, tool-backed feedback** rather than persuasive text.
- Security-conscious teams treating AI output as an **untrusted input** that must be validated.
- Builders who prefer an interactive UI while the automation surface area matures.

**Not for:**
- Teams without tests or basic static analysis (you won’t get signal without tooling).
- “One-click auto-merge AI changes” workflows.

---

## Try it (UI-first, 5 minutes)

### 1) Clone + install
```bash
git clone https://github.com/canstralian/CodeTuneStudio.git
cd CodeTuneStudio
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) (Optional) enable AI-powered plugins
```bash
export OPENAI_API_KEY="..."
# or:
export ANTHROPIC_API_KEY="..."
```

### 3) Run the app
Preferred:
```bash
codetune-studio
```

Compatibility/legacy:
```bash
python app.py
```

The app will start the Streamlit UI (default port is configured in the CLI/env settings).

---

## Security & operational expectations

- **No secrets in source control.** Use environment variables for API keys and database credentials.
- **Assume LLM output is untrusted.** It must be validated before it touches production workflows.
- **Least privilege by default.** Keep CI permissions minimal and pin third-party actions when possible.
- **Input validation first.** Any future pipeline that accepts repo paths, patches, or commands must harden against injection and unsafe filesystem behavior.

---

## Contribute (early builders)

If you want to shape the validation pipeline MVP:
- Issues: https://github.com/canstralian/CodeTuneStudio/issues
- Repo: https://github.com/canstralian/CodeTuneStudio

Suggested first contributions:
- add a sandboxed workspace runner (temp copy / git worktree)
- add subprocess-based runners for pytest/ruff/mypy with timeouts + parsed results
- add a Streamlit component to compare strategy results (pass/fail + logs)

---

## Roadmap snapshot (high-level)

- Validation pipeline MVP (diff → sandbox → tool-gated results → UI compare)
- Persisted execution history (once schemas stabilize)
- Headless orchestrator (enables future CLI + GitHub App integration)
