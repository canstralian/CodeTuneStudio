# Deprecated Copilot Guides Archive

This directory contains historical Copilot/Codex documentation that has been **deprecated and archived** as of 2025-12-13.

## Why These Files Were Deprecated

These six overlapping guides contained:
- Conflicting or duplicated guidance
- References to "Trading Bot Swarm" instead of the correct project name "CodeTuneStudio"
- Inconsistent formatting and structure
- Copy/paste pollution from other projects

## Current Documentation

Please use these canonical documentation sources instead:

### For Developers (Tool Setup, CI/CD, Workflows)
**[`docs/ai-assistant-guide.md`](../../ai-assistant-guide.md)**

This guide covers:
- GitHub Copilot subscription and IDE plugin installation
- Repository configuration (branch protection, required checks)
- Pre-commit hooks setup and usage
- CI/CD workflow best practices with security
- Troubleshooting common issues
- Developer workflow best practices

### For AI Agents (Behavioral Rules, Code Standards)
**[`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md)**

This document defines:
- Agent behavioral constraints and templates
- Async pattern mandates
- Security defaults (no secrets in logs, parameterized SQL)
- Logging standards (structured logs, correlation IDs)
- Code style enforcement (PEP 8, type hints)
- Database security requirements
- API security patterns

## Archived Files

The following files are preserved here for historical reference only:

1. `copilot-codex-guide.md` - Original configuration guide
2. `copilot_codex_guide.md` - Alternate configuration guide
3. `copilot_codex_comprehensive_guide.md` - Comprehensive guide version
4. `copilot_codex_configuration_guide.md` - Configuration-focused guide
5. `github-copilot-codex-guide.md` - GitHub-specific guide

**Note:** A sixth file (`Copilot_Codex_Guide.md`) mentioned in PR #150 was not found in the repository at the time of archival.

## Do Not Use These Files

⚠️ **WARNING:** The content in these archived files may be:
- Outdated
- Incorrect for CodeTuneStudio
- Conflicting with current standards
- Referencing wrong project names

Always refer to the canonical documentation listed above.

---

*Archived: 2025-12-13*  
*Archive Maintainer: CodeTuneStudio Contributors*
