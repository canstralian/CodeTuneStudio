# GitHub Copilot Instructions — CodeTuneStudio

These instructions define **mandatory constraints** for GitHub Copilot when generating, modifying, or reviewing content in this repository.

They exist to prevent documentation drift, duplication, and project identity errors.

---

## 1. Project Identity (Non-Negotiable)

- Project name: **CodeTuneStudio**
- Do NOT reference:
  - Trading Bot Swarm
  - Any legacy or external project names
- If an example, template, or snippet includes another project name, replace it with **CodeTuneStudio**.

---

## 2. Documentation Authority

- `docs/COPILOT_GUIDE.md` is the **single source of truth** for AI usage and guidance.
- Do NOT create new Copilot, Codex, or AI-related documentation files.
- Extend or refine existing documentation instead of introducing parallel guides.
- Prefer improving clarity in-place over adding new files.

---

## 3. File Creation & Deletion Rules

- Do NOT create new documentation files unless explicitly instructed.
- Before deleting or renaming documentation:
  - Check for inbound references in `README.md` and `docs/`
  - Update all affected links in the same change set
- Never leave broken or dangling documentation references.

---

## 4. Consolidation Bias

- Prefer **consolidation over proliferation**.
- If multiple documents cover overlapping topics:
  - Merge them into a single authoritative file
  - Remove redundant files after references are updated
- Fewer, clearer documents are preferred to many fragmented ones.

---

## 5. Link & Reference Integrity

- Verify that all referenced files exist.
- Use correct relative paths that match the current repository structure.
- Do NOT reference hypothetical, future, or non-existent files.

---

## 6. Documentation Style Constraints

- Tone: technical, concise, non-marketing
- Avoid redundancy and repetition
- Maintain internal consistency across all documentation
- Do NOT reintroduce deprecated terminology or structure

---

## 7. Uncertainty Failsafe

If uncertainty exists about:
- Documentation authority
- File ownership
- Structural changes

Then:
- Default to modifying the most central existing document
- Prefer clarification over assumption
- Avoid creating new sources of truth

---

## 8. Scope Discipline

- This repository favors **low-entropy changes**
- Do NOT introduce unnecessary files, concepts, or abstractions
- Every change should reduce confusion, not relocate it