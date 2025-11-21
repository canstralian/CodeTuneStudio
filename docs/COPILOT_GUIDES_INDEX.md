# GitHub Copilot & Codex Documentation Index

This index provides an overview of all GitHub Copilot and Codex related
documentation in this repository.

## Primary Documentation

### [COPILOT_CODEX_COMPREHENSIVE_GUIDE.md](COPILOT_CODEX_COMPREHENSIVE_GUIDE.md)

**Status:** ✅ **Active** - Current comprehensive guide  
**Version:** 1.0.0  
**Last Updated:** 2025-11-21

The main comprehensive guide for GitHub Copilot and Codex integration. This
document consolidates and enhances previous guides with complete coverage of:

- Configuration and setup for Copilot and Codex
- Testing and linting automation
- Code style standards (PEP 8 compliance)
- Security scanning methodologies
- Semantic release processes
- CI/CD integration
- Contributor expectations and workflows
- Maintenance procedures
- Troubleshooting guide
- Best practices summary

**Use this guide for:** All new contributors, development setup, CI/CD
configuration, and as the authoritative reference for project standards.

## Legacy Documentation

### [copilot_codex_guide.md](copilot_codex_guide.md)

**Status:** 📚 **Legacy** - Superseded by comprehensive guide  
**Lines:** 195

Original guide focusing on Trading Bot Swarm ecosystem. Content has been
incorporated into the comprehensive guide with enhancements.

**Historical Content:**
- Basic configuration overview
- Custom instruction behavior
- Workflow automation examples (lint, test, semantic release, security)
- Basic contributor guidelines

### [copilot_codex_configuration_guide.md](copilot_codex_configuration_guide.md)

**Status:** 📚 **Legacy** - Superseded by comprehensive guide  
**Lines:** 214

Secondary guide with additional details on configuration. Content has been
merged into the comprehensive guide.

**Historical Content:**
- Copilot as pair programmer concept
- Testing and linting standards
- Code style and security defaults
- Logging and observability
- Version control workflow

## Related Documentation

### Project Configuration

- [.github/copilot-instructions.md](../.github/copilot-instructions.md) -
  Active Copilot behavior instructions used by GitHub Copilot in the IDE

### Workflow Files

Located in `.github/workflows/`:

- `ci.yml` - Main CI pipeline with linting, testing, and building
- `python-style-checks.yml` - Additional Python style validation
- `release.yml` - Semantic release and PyPI publishing
- `huggingface-deploy.yml` - Model deployment to Hugging Face

### Contributing Guides

- [docs/ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [docs/CONTRIBUTING_CODE_QUALITY.md](CONTRIBUTING_CODE_QUALITY.md) - Code
  quality standards
- [docs/PLUGIN_GUIDE.md](PLUGIN_GUIDE.md) - Plugin development guide

## Migration Notes

If you were using the legacy guides (`copilot_codex_guide.md` or
`copilot_codex_configuration_guide.md`), please transition to the
comprehensive guide. Key improvements include:

1. **Enhanced Security Section**: Expanded coverage of secrets management,
   input validation, and database security
2. **Detailed Testing Guidelines**: Comprehensive testing standards with
   examples
3. **Complete CI/CD Integration**: Full workflow documentation with
   troubleshooting
4. **Semantic Release Process**: Detailed conventional commits and versioning
5. **Troubleshooting Guide**: Common issues and solutions
6. **Best Practices Summary**: Quick reference checklists

## Quick Start

For new contributors:

1. Read [COPILOT_CODEX_COMPREHENSIVE_GUIDE.md](COPILOT_CODEX_COMPREHENSIVE_GUIDE.md)
   sections:
   - Purpose and Scope
   - Copilot as a Disciplined Pair Programmer
   - Contributor Expectations

2. Set up development environment following the guide's instructions

3. Review [.github/copilot-instructions.md](../.github/copilot-instructions.md)
   for IDE-specific Copilot behavior

4. Follow the Contributing Workflow section for your first PR

## Maintenance

This index and the comprehensive guide are reviewed quarterly. Next review due:
**2026-02-21**

For questions or suggestions about these guides, please open an issue with the
label `documentation`.

---

**Last Updated:** 2025-11-21  
**Maintained by:** [@canstralian](https://github.com/canstralian)
