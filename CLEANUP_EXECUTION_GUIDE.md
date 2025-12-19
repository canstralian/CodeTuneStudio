# Repository Cleanup Execution Guide

**Date:** 2025-12-19
**Repository:** CodeTuneStudio
**Approach:** Conservative, Observable, Reversible

## Philosophy

This cleanup follows the principle that **repository maintenance is systems engineering, not housekeeping**. Every action is:
- **Documented**: No silent closures
- **Communicative**: Contributors are notified before action
- **Reversible**: Nothing is deleted permanently
- **Time-bound**: Grace periods for response
- **Objective**: Based on measurable criteria

## Current State

- **Open PRs:** 83
- **Open Issues:** 2
- **Status:** High-drift, low-volume scenario

## Cleanup Protocol

### Phase 1: Inventory and Label (Week 1)

#### Step 1.1: Label Stale PRs
For each PR that meets stale criteria:
- Age > 60 days AND no activity in last 30 days
- OR failing checks/merge conflicts for 30+ days
- OR marked as WIP/draft with no activity in 30+ days

**Action:**
```bash
# Add label "stale-pr" to candidate PRs
gh pr edit <PR_NUMBER> --add-label "stale-pr"
```

**Criteria Table:**

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Age without activity | 60+ days | Conversation has likely ended |
| Merge conflicts | 30+ days | Requires contributor attention |
| Failing checks | 30+ days | Not merge-ready |
| WIP/Draft status | 30+ days inactive | Indicates abandoned work |
| Superseded | Any age | Functionality exists elsewhere |

#### Step 1.2: Label Stale Issues
For each issue that meets stale criteria:
- Age > 90 days AND no activity after clarification request (14+ days)
- OR missing reproduction steps after request (30+ days)
- OR no labels/triage after 90 days

**Action:**
```bash
# Add label "stale-issue" to candidate issues
gh issue edit <ISSUE_NUMBER> --add-label "stale-issue"
```

### Phase 2: Communication (Week 1-2)

#### Step 2.1: Ping PR Authors
For each stale PR, add a comment using this template:

```markdown
👋 Hi @contributor!

This pull request has been labeled as potentially stale because:
- [X] No activity in the last 30+ days
- [ ] Merge conflicts present
- [ ] Failing checks
- [ ] Marked as WIP/draft

**If you'd like to keep this PR open, please:**
1. Add a comment confirming you're still working on it
2. Push new commits to update the PR
3. Request a review if it's ready

**Grace period:** 14 days from today (until YYYY-MM-DD — replace with the actual date when posting, e.g., 2025-12-31)

If we don't hear back, we'll close this PR to keep our queue manageable. You can always reopen it or create a fresh PR later!

Thank you for your contribution! 🙏

---
_Part of repository cleanup initiative. See CLEANUP_EXECUTION_GUIDE.md for details._
```

#### Step 2.2: Ping Issue Authors
For each stale issue, add a comment using this template:

```markdown
👋 Hi @reporter!

This issue has been labeled as potentially stale because:
- [X] No activity in the last 60+ days
- [ ] Missing reproduction steps after request
- [ ] No triage/labels after initial report

**To keep this issue open, please:**
1. Confirm it's still relevant
2. Provide reproduction steps if requested
3. Add any additional context

**Grace period:** 14 days from today (until YYYY-MM-DD) <!-- Replace YYYY-MM-DD with the actual date before posting -->

If we don't hear back, we'll close this issue to reduce noise. You can always reopen it or create a fresh issue with updated details!

Thank you for reporting! 🙏

---
_Part of repository cleanup initiative. See CLEANUP_EXECUTION_GUIDE.md for details._
```

### Phase 3: Grace Period (Week 2-3)

**Wait 14 days** from communication date.

During this period:
- Monitor for responses
- Remove "stale" label if contributor responds
- Keep a log of responses

**Response tracking spreadsheet format:**
```csv
Type,Number,Title,Labeled Date,Response Date,Status,Action
PR,123,Fix bug,2025-12-19,2025-12-22,Responded,Keep Open
PR,124,Add feature,2025-12-19,,No Response,Close
Issue,125,Bug report,2025-12-19,2025-12-21,Responded,Keep Open
```

### Phase 4: Closure (Week 4)

#### Step 4.1: Close Unresponsive PRs
For PRs with no response after grace period:

```markdown
Closing this pull request due to inactivity (no response within 14-day grace period).

**This is not a rejection of your work!**

If you'd like to revive this PR:
1. Rebase your branch on the latest `main`
2. Resolve any conflicts
3. Either:
   - Comment here to reopen, OR
   - Open a fresh PR and reference this one

**Why we're doing this:**
We're cleaning up stale PRs to keep the repository manageable and ensure active work gets proper attention. See CLEANUP_EXECUTION_GUIDE.md for our full protocol.

Thank you for your contribution! 🙏

---
_Closed as part of repository maintenance initiative._
```

**Action:**
```bash
# Close PR with comment
gh pr close <PR_NUMBER> --comment "$(cat closure_message.txt)"

# Do NOT delete the branch immediately
# Branches can be deleted after 30 days if PR remains closed
```

#### Step 4.2: Close Unresponsive Issues
For issues with no response after grace period:

```markdown
Closing this issue due to inactivity (no response within 14-day grace period).

If this issue is still relevant:
1. Comment here with updated details, OR
2. Open a fresh issue and reference this one

We'll happily reopen if you provide:
- Current reproduction steps (for bugs)
- Updated context (for feature requests)
- Confirmation it still affects the latest version

**Why we're doing this:**
We're cleaning up stale issues to focus on active problems and requests. See CLEANUP_EXECUTION_GUIDE.md for our full protocol.

Thank you for your report! 🙏

---
_Closed as part of repository maintenance initiative._
```

**Action:**
```bash
# Close issue with comment
gh issue close <ISSUE_NUMBER> --comment "$(cat closure_message.txt)"
```

### Phase 5: Projects Cleanup (Week 4-5)

#### Step 5.1: Audit Projects
```bash
# List all projects
gh project list

# For each project, check:
# 1. Last updated date
# 2. Number of cards
# 3. Link to active issues/PRs
```

#### Step 5.2: Archive Inactive Projects
Criteria for archiving:
- No updates in last 6 months
- Most cards linked to closed issues/PRs
- Workflow no longer matches current practice

**Action:**
```bash
# Archive project (not delete)
gh project archive <PROJECT_NUMBER>
```

#### Step 5.3: Normalize Active Projects
For projects still in use:
1. Consolidate duplicate columns
2. Update project description
3. Document workflow in README

**Recommended minimal column set:**
- **Backlog**: Triaged but not started
- **In Progress**: Actively being worked on
- **Review**: Awaiting review/feedback
- **Done**: Completed (auto-clear weekly)

## Specific PR Categorization

### Tier 1: Close After Communication (High Confidence)

These PRs meet multiple stale criteria:

**Security Autofix PRs (3 PRs):**
- PR #28, #35, #53: 2+ months old, automated fixes, likely superseded
- **Rationale:** Security should use fresh fixes

**Very Old PRs (15-20 PRs from Sept-Oct):**
- PRs from September: #5, #21, #25, #26
- PRs from early October: #33, #36-#43, #45, #46, #50, #53, #55, #59
- **Rationale:** 2-3 months old, codebase has moved on

**WIP/Report PRs (4 PRs):**
- PR #21 (marked [WIP]), #125 (situation report), #131 (marked [WIP]), #143 (task list)
- **Rationale:** Not code changes or explicitly incomplete

**Merge Conflict Resolution PRs (3 PRs):**
- PR #92, #106, #107: Resolving conflicts in already-stale PRs
- **Rationale:** Original PRs are being closed

### Tier 2: Close After Review (Medium Confidence)

These PRs are redundant but may have unique contributions:

**Duplicate Documentation (8-10 PRs):**
- Keep: PR #157 (most comprehensive recent)
- Close after review: #99, #103, #105, #118, #119, #121, #151, #152, #153

**Duplicate CI/CD (4 PRs):**
- Keep: PR #158 (most recent)
- Close after review: #96, #97, #111, #144

**Duplicate Formatting (5 PRs):**
- Keep: PR #162 or #163 (most recent)
- Close after review: #33, #55, #59, #108, #156

**Duplicate Dependencies (5-6 PRs):**
- Keep: Most comprehensive recent PR (needs identification)
- Close after review: #82, #109, #110, #112, #124, #126

**Duplicate Refactoring (3 PRs):**
- Keep: One comprehensive PR (needs review to determine which)
- Close after review: Others from #93, #94, #116, #117

### Tier 3: Careful Review Required

**Dependabot PRs (6-8 PRs):**
- PRs #69, #73, #75, #76, #87, #114, #160, #161
- **Action:** Check if tests pass, merge if yes, close if superseded

**Recent PRs (5 PRs):**
- PRs #162, #163, #165, #166 (from Dec 13-19)
- **Action:** Review individually, likely keep open

### Tier 4: Keep Open

**Active Recent Work:**
- Any PR with activity in last 14 days
- Any PR with passing checks and no conflicts
- Any PR labeled "keep-open" or "in-progress"

## Automation Setup

After manual cleanup, implement automation:

1. **Enable Stale Bot** (already created: `.github/workflows/stale-pr-management.yml`)
   - 30-day stale threshold for PRs
   - 60-day stale threshold for issues
   - 14-day grace period before auto-close

2. **Create PR Template** (see below)

3. **Create Issue Templates** (see below)

4. **Enable GitHub Discussions** (optional)
   - Move open-ended questions out of issues

## Success Metrics

**Immediate (Post-Cleanup):**
- Open PR count: 83 → 8-15
- PR age (median): 30+ days → <14 days
- Merge conflict rate: ~40% → <10%

**Long-term (3-6 months):**
- Stale PR rate: <10%
- Average time to close: <30 days
- Contributor satisfaction: Measured via survey

## Logging and Tracking

Create a cleanup log: `CLEANUP_LOG.md`

Format:
```markdown
## Cleanup Execution Log

### Phase 1: Labeling
- Date: 2025-12-19
- PRs labeled: 65
- Issues labeled: 1

### Phase 2: Communication
- Date: 2025-12-20
- PRs notified: 65
- Issues notified: 1

### Phase 3: Grace Period
- Start: 2025-12-20
- End: 2026-01-03
- Responses received: TBD

### Phase 4: Closure
- Date: 2026-01-03
- PRs closed: TBD
- Issues closed: TBD
- Reopens requested: TBD
```

## Rollback Plan

If cleanup is too aggressive:

1. **Reopen closed PRs:**
   ```bash
   gh pr reopen <PR_NUMBER>
   gh pr comment <PR_NUMBER> --body "Reopened. We apologize for the inconvenience."
   ```

2. **Remove stale labels:**
   ```bash
   gh pr edit <PR_NUMBER> --remove-label "stale-pr"
   ```

3. **Post apology notice:**
   - Create issue explaining the situation
   - Link to reopened PRs/issues
   - Adjust protocol for next cleanup

## Communication Channels

Announce cleanup initiative:

1. **Repository README** (add banner):
   ```markdown
   > 🧹 **Repository Cleanup in Progress**: We're cleaning up stale PRs and issues to improve maintainability. See [CLEANUP_EXECUTION_GUIDE.md] for details. Have questions? Open a discussion!
   ```

2. **Pinned Issue** (create):
   ```markdown
   # 🧹 Repository Cleanup Initiative

   We're performing a systematic cleanup of stale PRs and issues. This is not a rejection of contributions, but a way to keep our repository healthy and manageable.

   **Timeline:**
   - Phase 1 (Labeling): Week of Dec 19
   - Phase 2 (Communication): Week of Dec 23
   - Phase 3 (Grace Period): Dec 23 - Jan 6
   - Phase 4 (Closure): Week of Jan 6

   **Full Protocol:** See [CLEANUP_EXECUTION_GUIDE.md]

   **Questions?** Comment below!
   ```

3. **Contributors** (individual mentions):
   - Use @ mentions in cleanup comments
   - Send follow-up if contributor has multiple stale PRs

## Post-Cleanup

After cleanup is complete:

1. **Document lessons learned** in `CLEANUP_LOG.md`
2. **Update CONTRIBUTING.md** with PR/issue lifecycle expectations
3. **Enable automation** to prevent future drift
4. **Schedule quarterly reviews** to maintain health

## Appendix: Command Reference

```bash
# List all open PRs sorted by last updated
gh pr list --state open --json number,title,updatedAt --limit 100 | jq -r 'sort_by(.updatedAt) | .[] | "\(.number): \(.title) (updated: \(.updatedAt))"'

# Add stale label
gh pr edit <PR_NUMBER> --add-label "stale-pr"

# Remove stale label
gh pr edit <PR_NUMBER> --remove-label "stale-pr"

# Add comment
gh pr comment <PR_NUMBER> --body "Your message here"

# Close PR
gh pr close <PR_NUMBER>

# Reopen PR
gh pr reopen <PR_NUMBER>

# Same commands work for issues, replace 'pr' with 'issue'
```

---

**Remember:** The goal is a healthy repository where active work gets attention and stale work doesn't create noise. Every closure is an invitation to return when the time is right.
