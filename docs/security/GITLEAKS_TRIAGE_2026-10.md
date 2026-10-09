# Gitleaks Triage — October 2026

**Source:** `Security OS` workflow run 37258257359 (scheduled, `main` @ `9579afc`, 2026-10-05), job *Secret Scan · Credential Leak Detection*. Gitleaks reported `leaks found: 20` across 596 commits, output redacted.
**Method:** Each redacted hit was resolved by reading the real value at the reported commit/line in a full (unshallowed) clone. A second regex sweep of full history on all 146 remote branches looked for provider-shaped tokens (GitHub, Anthropic, OpenAI, Hugging Face, AWS, PyPI, Slack, Google, private keys, Sentry DSNs).

## Verdict

| Group | Hits | Actual value | Live? |
|---|---|---|---|
| Docs "never do this" examples (`docs/*.md`, `.github/copilot-instructions.md`) | 7 | `sk-1234567890abcdef` / `sk-1234567890` | No — placeholder |
| Logging redaction tests/demo (`tests/test_logging.py`, `LOGGING.md`, `examples/logging_demo.py`) | 3 | `sk-1234567890[abcdef]` | No — placeholder |
| Rules-engine test fixture (`tests/ai_review_gate/test_rules_engine.py`) | 1 | `sk-1234567890abcdef` | No — placeholder |
| `codex/templates/SECRETS.md` | 1 | `pypi-AgEIcHlwaS5vcmc...` — the fixed base64 prefix every PyPI token shares, truncated | No — no token body |
| `.secrets.baseline` (`hashed_secret`) | 8 | detect-secrets SHA-1 hashes; source values are `password`, `password123`, `pass`, `sk-1234567890abcdef`, `fake_key`, `test_api_key` | No — hashes of placeholders |

**All 20 Gitleaks findings are false positives.** Nothing among them needs rotation. They are listed by fingerprint in `/.gitleaksignore`.

## Missed by Gitleaks — real credential

| Item | Location | Exposure |
|---|---|---|
| Sentry DSN (public client key + org/project) hardcoded as `DEFAULT_SENTRY_DSN` | `core/monitoring.py`, commit `505ff61` (2026-08-03), branch `claude/sentry-tracing-setup-hljqj6` (PR #377). Removed from the tip in `70eb17a`, still in branch history. | Public repo since 2026-08-03. Not on `main` or any tag. |

Gitleaks missed it because the URL is split across two string literals.

**Impact:** A Sentry DSN is a write-only ingest key. It cannot read data. The risk is event spoofing and quota exhaustion on that project.

**Action — rotate before any history cleanup:** In Sentry, go to Project Settings → Client Keys (DSN). Create a new key, set it via the `SENTRY_DSN` env var wherever it is used, then **disable/delete the old key**. Once the old key is revoked, branch-history cleanup is cosmetic. That cleanup can be done by deleting or squash-merging the PR #377 branch.
