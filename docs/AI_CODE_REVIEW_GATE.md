# AI Code Review Gate Architecture

## Overview

The AI Code Review Gate is a drop-in CI/CD check for GitHub Actions that reviews pull requests like a senior engineer and fails the build when code violates agreed-upon standards for safety, clarity, and maintainability—**without ever modifying code automatically**.

## Core Principles

### What It Does
- ✅ Reviews code changes in pull requests
- ✅ Identifies violations of safety, clarity, and maintainability standards
- ✅ Provides clear explanations of what's wrong and why it matters
- ✅ Suggests diffs that developers can apply manually
- ✅ Explicitly refuses review when context is insufficient
- ✅ Fails CI builds when critical issues are found

### What It Doesn't Do
- ❌ **Never** auto-applies fixes or modifies code
- ❌ **Never** commits changes automatically
- ❌ **Never** makes silent edits
- ❌ **Never** operates on "vibes" - all decisions are explicit and explained

## Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Pull Request                       │
└──────────────────┬──────────────────────────────────────────┘
                   │ Trigger Event
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions Workflow                         │
│  (.github/workflows/ai-code-review-gate.yml)                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Review Orchestrator                             │
│         (scripts/ai_review_gate/orchestrator.py)            │
│                                                              │
│  • Fetches PR diff                                           │
│  • Checks context sufficiency                                │
│  • Coordinates review process                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌─────────────────┐   ┌─────────────────────┐
│  Context Gate   │   │   Review Engine     │
│  (context.py)   │   │   (reviewer.py)     │
│                 │   │                     │
│ • Check file    │   │ • Safety checks     │
│   changes size  │   │ • Clarity analysis  │
│ • Verify diff   │   │ • Maintainability   │
│   clarity       │   │ • LLM integration   │
│ • Detect        │   │                     │
│   ambiguity     │   └─────────┬───────────┘
│                 │             │
│ If insufficient │             │
│ context:        │             ▼
│ REFUSE + FAIL   │   ┌─────────────────────┐
└─────────────────┘   │  Rules Engine       │
                      │  (rules.py)         │
                      │                     │
                      │ • Security rules    │
                      │ • Code quality      │
                      │ • Best practices    │
                      └─────────┬───────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │  Diff Generator     │
                      │  (diff_gen.py)      │
                      │                     │
                      │ • Parse violations  │
                      │ • Generate fixes    │
                      │ • Format as diffs   │
                      └─────────┬───────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │  Output Formatter   │
                      │  (formatter.py)     │
                      │                     │
                      │ • Format report     │
                      │ • Create summary    │
                      │ • Add context       │
                      └─────────┬───────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │  GitHub Integration │
                      │  (github_api.py)    │
                      │                     │
                      │ • Post PR comment   │
                      │ • Set check status  │
                      │ • Add annotations   │
                      └─────────────────────┘
```

## Component Details

### 1. GitHub Actions Workflow

**File**: `.github/workflows/ai-code-review-gate.yml`

**Responsibilities**:
- Trigger on PR events (opened, synchronize, reopened)
- Check out code with full PR context
- Set up Python environment
- Install dependencies
- Execute review orchestrator
- Handle exit codes (0 = pass, 1 = fail with violations, 2 = insufficient context)

**Configuration**:
```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  FAIL_ON_INSUFFICIENT_CONTEXT: true
  STRICT_MODE: true  # Fail on warnings, not just errors
```

### 2. Review Orchestrator

**File**: `scripts/ai_review_gate/orchestrator.py`

**Responsibilities**:
- Coordinate the entire review process
- Fetch PR metadata and diff from GitHub API
- Route to context gate for sufficiency check
- Pass to review engine if context is sufficient
- Handle errors and retries
- Aggregate results and determine final status

**Key Functions**:
```python
def orchestrate_review(pr_number: int, repo: str) -> ReviewResult:
    """Main entry point for review process."""

def fetch_pr_changes(pr_number: int, repo: str) -> PRChanges:
    """Fetch diff and metadata from GitHub."""

def determine_exit_code(result: ReviewResult) -> int:
    """Convert review result to exit code."""
```

### 3. Context Gate

**File**: `scripts/ai_review_gate/context.py`

**Responsibilities**:
- Determine if there's sufficient context to perform a meaningful review
- Explicitly refuse when context is insufficient
- Provide clear refusal messages

**Refusal Criteria**:
- PR diff is too large (>5000 lines changed)
- Changes span too many unrelated files (>50 files)
- Critical files missing context (e.g., only seeing usage, not definition)
- Binary files or generated code without source
- Incomplete diff (GitHub API truncation)

**Key Functions**:
```python
def check_context_sufficiency(changes: PRChanges) -> ContextCheck:
    """Determine if context is sufficient for review."""

def generate_refusal_message(reason: str) -> str:
    """Create explicit refusal message."""
```

**Example Refusal**:
```
⛔ INSUFFICIENT CONTEXT FOR REVIEW

This PR cannot be reviewed due to: Excessive changes (8,432 lines across 127 files)

To enable review:
- Split this PR into smaller, focused changes
- Each PR should address a single concern
- Limit to <5000 lines and <50 files per PR

The build will FAIL until the PR is split into reviewable units.
```

### 4. Review Engine

**File**: `scripts/ai_review_gate/reviewer.py`

**Responsibilities**:
- Core code analysis logic
- Integration with LLM (Anthropic Claude Sonnet 4.5)
- Apply rules engine to detect violations
- Generate findings with severity levels

**Review Categories**:
1. **Safety** (Critical - Always Fails Build)
   - SQL injection vulnerabilities
   - XSS/injection attacks
   - Hardcoded secrets/credentials
   - Insecure deserialization
   - Authentication/authorization bypasses

2. **Clarity** (Warning - Fails in Strict Mode)
   - Unclear variable/function names
   - Missing or inadequate docstrings
   - Complex logic without comments
   - Magic numbers without explanation

3. **Maintainability** (Warning - Fails in Strict Mode)
   - Code duplication
   - Excessive complexity (cyclomatic complexity >10)
   - Tight coupling
   - Missing error handling
   - Inconsistent style

**Key Functions**:
```python
def review_changes(changes: PRChanges, rules: RuleSet) -> List[Finding]:
    """Perform AI-powered code review."""

def analyze_with_llm(code: str, context: str) -> LLMAnalysis:
    """Use LLM to analyze code for issues."""
```

### 5. Rules Engine

**File**: `scripts/ai_review_gate/rules.py`

**Responsibilities**:
- Define review rules as code
- Categorize rules by severity
- Support custom project-specific rules

**Rule Structure**:
```python
@dataclass
class Rule:
    id: str
    category: Literal["safety", "clarity", "maintainability"]
    severity: Literal["critical", "warning", "info"]
    description: str
    pattern: Optional[str]  # Regex or AST pattern
    llm_prompt: Optional[str]  # For AI-based detection

    def check(self, code: str, context: Dict) -> Optional[Violation]:
        """Check if this rule is violated."""
```

**Example Rules**:
```python
SECURITY_RULES = [
    Rule(
        id="SEC001",
        category="safety",
        severity="critical",
        description="SQL injection: raw SQL with string concatenation",
        pattern=r'execute\s*\(\s*["\'].*\+.*["\']',
        llm_prompt="Check for SQL injection vulnerabilities"
    ),
    Rule(
        id="SEC002",
        category="safety",
        severity="critical",
        description="Hardcoded credentials detected",
        pattern=r'(password|api_key|secret|token)\s*=\s*["\'][^"\']+["\']',
        llm_prompt=None  # Pattern-based only
    )
]
```

### 6. Diff Generator

**File**: `scripts/ai_review_gate/diff_gen.py`

**Responsibilities**:
- Generate suggested fixes as unified diffs
- Format diffs for manual application
- **Never** apply diffs automatically

**Key Functions**:
```python
def generate_fix_diff(violation: Violation, original: str) -> str:
    """Generate unified diff for suggested fix."""

def format_diff_for_display(diff: str) -> str:
    """Format diff with syntax highlighting for display."""
```

**Example Output**:
```diff
--- a/app.py
+++ b/app.py
@@ -45,7 +45,8 @@ def get_user(user_id):
-    query = f"SELECT * FROM users WHERE id = {user_id}"
-    result = db.execute(query)
+    # Use parameterized query to prevent SQL injection
+    query = "SELECT * FROM users WHERE id = ?"
+    result = db.execute(query, (user_id,))
     return result.fetchone()
```

### 7. Output Formatter

**File**: `scripts/ai_review_gate/formatter.py`

**Responsibilities**:
- Format review findings as markdown
- Create clear, actionable reports
- Include severity indicators
- Add links to documentation

**Key Functions**:
```python
def format_review_result(result: ReviewResult) -> str:
    """Format complete review result as markdown."""

def format_finding(finding: Finding) -> str:
    """Format individual finding with context."""
```

**Example Output**:
```markdown
## 🔴 AI Code Review - FAILED

**3 critical issues found** - Build failed

### Critical Issues (Must Fix)

#### 🚨 SEC001: SQL Injection Vulnerability
**File**: `app.py:45-47`
**Severity**: Critical

**Issue**:
Raw SQL query using string concatenation detected. This creates a SQL injection vulnerability.

```python
query = f"SELECT * FROM users WHERE id = {user_id}"
result = db.execute(query)
```

**Why this matters**:
An attacker can inject malicious SQL by passing a crafted `user_id` value like `1 OR 1=1`, potentially accessing or modifying unauthorized data.

**Suggested Fix**:
```diff
--- a/app.py
+++ b/app.py
@@ -45,7 +45,8 @@ def get_user(user_id):
-    query = f"SELECT * FROM users WHERE id = {user_id}"
-    result = db.execute(query)
+    # Use parameterized query to prevent SQL injection
+    query = "SELECT * FROM users WHERE id = ?"
+    result = db.execute(query, (user_id,))
     return result.fetchone()
```

**How to apply**:
1. Review the suggested diff above
2. Apply changes manually to `app.py`
3. Verify the fix with tests
4. Push updated code

📚 **Learn more**: [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)

---

### Summary

- ✅ **0** files passed review
- ⚠️ **3** files have critical issues
- 📝 **2** warnings (will fail in strict mode)

**Next Steps**:
1. Address all critical issues listed above
2. Apply suggested fixes manually
3. Run local tests: `pytest tests/`
4. Push updated code to re-trigger review
```

### 8. GitHub Integration

**File**: `scripts/ai_review_gate/github_api.py`

**Responsibilities**:
- Post review comments to PR
- Set commit status checks
- Add file annotations for violations
- Update check run status

**Key Functions**:
```python
def post_review_comment(pr_number: int, repo: str, body: str) -> None:
    """Post formatted review as PR comment."""

def set_check_status(commit_sha: str, status: str, summary: str) -> None:
    """Set GitHub check run status."""

def add_file_annotations(findings: List[Finding]) -> None:
    """Add inline annotations to changed files."""
```

## Configuration

### Environment Variables

**Required**:
- `ANTHROPIC_API_KEY`: API key for Claude (Sonnet 4.5)
- `GITHUB_TOKEN`: GitHub token for API access (auto-provided in Actions)

**Optional**:
- `FAIL_ON_INSUFFICIENT_CONTEXT`: Fail build when context insufficient (default: `true`)
- `STRICT_MODE`: Fail on warnings, not just errors (default: `false`)
- `MAX_FILES_PER_PR`: Maximum files to review (default: `50`)
- `MAX_LINES_PER_PR`: Maximum lines changed (default: `5000`)
- `CUSTOM_RULES_PATH`: Path to custom project rules (default: none)

### Custom Rules

Projects can define custom rules in `.ai-review-rules.yml`:

```yaml
rules:
  - id: PROJ001
    category: maintainability
    severity: warning
    description: "All API endpoints must have rate limiting"
    pattern: "@app.route.*\n.*def.*:"
    llm_prompt: "Check if this Flask route has rate limiting decorator"

  - id: PROJ002
    category: clarity
    severity: warning
    description: "Functions must have type hints"
    llm_prompt: "Check if function has complete type hints for parameters and return"
```

## Data Flow

### Successful Review (Pass)

```
1. PR opened/updated
2. Workflow triggers
3. Orchestrator fetches changes
4. Context gate: sufficient ✓
5. Review engine analyzes code
6. No critical issues found
7. Format: "✅ All checks passed"
8. Post comment to PR
9. Set check status: success
10. Build continues
```

### Successful Review (Fail - Violations Found)

```
1. PR opened/updated
2. Workflow triggers
3. Orchestrator fetches changes
4. Context gate: sufficient ✓
5. Review engine analyzes code
6. Critical issues found (3 violations)
7. Diff generator creates fixes
8. Format: "🔴 3 critical issues"
9. Post detailed comment with diffs
10. Set check status: failure
11. Build FAILS ❌
```

### Insufficient Context (Refuse + Fail)

```
1. PR opened/updated (8,432 lines, 127 files)
2. Workflow triggers
3. Orchestrator fetches changes
4. Context gate: INSUFFICIENT ❌
5. Generate refusal message
6. Format: "⛔ INSUFFICIENT CONTEXT"
7. Post refusal message
8. Set check status: failure
9. Build FAILS ❌
```

## Exit Codes

The review gate uses specific exit codes to communicate results:

- **0**: Review passed - no violations found
- **1**: Review failed - critical violations found
- **2**: Review refused - insufficient context
- **3**: Review error - system error (API failure, etc.)

## Testing Strategy

### Unit Tests
- Test individual components (rules, diff generation, formatting)
- Mock LLM responses for deterministic testing
- Test refusal logic with edge cases

### Integration Tests
- Test full review flow with sample PRs
- Verify GitHub API interactions (using fixtures)
- Test exit code handling

### E2E Tests
- Create test PRs in a test repository
- Verify actual workflow execution
- Validate comment formatting and annotations

### Test Files
```
tests/
├── unit/
│   ├── test_context_gate.py
│   ├── test_rules_engine.py
│   ├── test_diff_generator.py
│   └── test_formatter.py
├── integration/
│   ├── test_orchestrator.py
│   ├── test_reviewer.py
│   └── test_github_api.py
└── e2e/
    └── test_workflow.py
```

## Security Considerations

### API Key Protection
- Store Anthropic API key as GitHub secret
- Never log API keys or tokens
- Rotate keys periodically

### Code Exposure
- Be cautious about sending proprietary code to external LLM APIs
- Consider self-hosted LLM option for sensitive codebases
- Implement filtering for known secrets before sending to LLM

### Rate Limiting
- Implement retry logic with exponential backoff
- Cache LLM responses for unchanged code
- Set reasonable request timeouts

## Future Enhancements

### Phase 2
- Support for GitLab and Bitbucket
- Configurable severity thresholds per project
- Learning from accepted/rejected suggestions
- Integration with SAST tools (Bandit, Semgrep)

### Phase 3
- Support for multiple LLM providers (OpenAI, local models)
- Custom fine-tuned models for project-specific patterns
- Historical trend analysis and metrics dashboard
- Automated learning from code review feedback

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- GitHub Checks API: https://docs.github.com/en/rest/checks
- Anthropic Claude API: https://docs.anthropic.com/
- SYSTEM.md: Contract definitions and guarantees
