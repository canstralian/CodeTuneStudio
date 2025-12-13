# Deprecated Copilot Guides Archive

## Why These Files Were Archived

This directory contains historical Copilot/Codex configuration guides that have been deprecated due to:

1. **Documentation Sprawl**: Six overlapping guides with redundant content
2. **Copy/Paste Pollution**: Files contained references to non-existent projects ("Trading Bot Swarm")
3. **Inconsistent Standards**: Each file proposed slightly different practices
4. **Maintenance Burden**: Multiple guides became out of sync with actual project practices

## Current Documentation

These archived guides have been **replaced** by a two-tier documentation architecture:

### For Developers
**[`docs/ai-assistant-guide.md`](../../ai-assistant-guide.md)**
- Complete developer workflow for using AI coding assistants
- Stack reality check (Flask/Streamlit, PostgreSQL/SQLite, PyTorch)
- Enforced CI/CD workflows and required checks
- Local pre-flight commands matching CI
- Branch protection guidance

### For AI Agents
**[`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md)**
- Agent-facing behavioral rules and guardrails
- Security-first requirements (no hardcoded secrets, parameterized SQL)
- Code style enforcement (Black, Flake8, Ruff, MyPy)
- Async patterns and structured logging standards
- YAML behavioral template for AI assistants

## Archived Files

- `copilot-codex-guide.md` - Original guide with "Trading Bot Swarm" references
- `copilot_codex_guide.md` - Duplicate with slightly different content
- `copilot_codex_comprehensive_guide.md` - Extended version with overlap
- `copilot_codex_configuration_guide.md` - Another variant with CI anti-patterns
- `github-copilot-codex-guide.md` - Yet another overlapping guide

All archived files have been updated with redirect headers pointing to the current documentation.

## Timeline

- **Pre-2025**: Multiple guides created independently, causing confusion
- **PR #150**: Proposed adding a 6th guide with more "Trading Bot Swarm" content
- **2025-12-13**: Archived all redundant guides; implemented two-tier architecture

---

*For questions about this archival decision, see the PR that implemented the two-tier documentation architecture.*
