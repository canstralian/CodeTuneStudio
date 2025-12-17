"""
Output Formatter - Formats review results as clear, actionable markdown reports.

Creates human-readable reports with:
- Clear issue descriptions
- Why each issue matters
- Suggested fixes as diffs
- Instructions for manual application
"""

import logging
from typing import List, Dict
from datetime import datetime
from .types import ReviewResult, Finding, ReviewStatus, Severity, Category

logger = logging.getLogger(__name__)


class OutputFormatter:
    """
    Formats review results for display in GitHub PR comments and artifacts.
    """

    def format_review_result(self, result: ReviewResult) -> str:
        """
        Format complete review result as markdown.

        Args:
            result: Review result to format

        Returns:
            Formatted markdown report
        """
        if result.status == ReviewStatus.REFUSED:
            return self._format_refusal(result)
        elif result.status == ReviewStatus.ERROR:
            return self._format_error(result)
        elif result.status == ReviewStatus.PASSED:
            return self._format_success(result)
        else:  # FAILED
            return self._format_failure(result)

    def _format_success(self, result: ReviewResult) -> str:
        """Format successful review (no issues)."""
        report = f"""## ✅ AI Code Review - PASSED

**All checks passed!** No critical issues or warnings found.

### Review Summary

- **Files reviewed**: {result.pr_changes.file_count}
- **Lines analyzed**: {result.pr_changes.total_changes}
- **Execution time**: {result.execution_time:.2f}s

### Next Steps

Your code looks good! Once other CI checks pass, this PR is ready for human review.

---
*Reviewed by AI Code Review Gate v0.1.0*
*Timestamp: {result.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}*
"""
        return report

    def _format_failure(self, result: ReviewResult) -> str:
        """Format failed review (issues found)."""
        critical_count = result.summary.get("critical", 0)
        warning_count = result.summary.get("warnings", 0)

        # Header with status
        if critical_count > 0:
            header = f"## 🔴 AI Code Review - FAILED\n\n**{critical_count} critical issue(s) found** - Build failed\n"
        else:
            header = f"## ⚠️ AI Code Review - WARNINGS\n\n**{warning_count} warning(s) found** - Build failed (strict mode)\n"

        # Summary section
        summary = f"""
### Summary

- ✅ **{result.summary.get('files_reviewed', 0)}** files reviewed
- 🔴 **{critical_count}** critical issues
- ⚠️ **{warning_count}** warnings
- ℹ️ **{result.summary.get('info', 0)}** informational

"""

        # Findings sections
        critical_section = self._format_findings_by_severity(
            result.findings, Severity.CRITICAL
        )
        warning_section = self._format_findings_by_severity(
            result.findings, Severity.WARNING
        )
        info_section = self._format_findings_by_severity(
            result.findings, Severity.INFO
        )

        # Footer
        footer = f"""
---

### How to Proceed

1. **Review each issue** listed above
2. **Apply suggested fixes manually** - review diffs carefully before applying
3. **Run local tests**: `pytest tests/`
4. **Push updated code** to re-trigger review

**Build will remain FAILED until critical issues are resolved.**

---
*Reviewed by AI Code Review Gate v0.1.0*
*Execution time: {result.execution_time:.2f}s*
*Timestamp: {result.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}*
"""

        return (
            header
            + summary
            + critical_section
            + warning_section
            + info_section
            + footer
        )

    def _format_refusal(self, result: ReviewResult) -> str:
        """Format refusal message."""
        report = f"""## ⛔ AI Code Review - INSUFFICIENT CONTEXT

**This PR cannot be reviewed automatically.**

**Reason:** {result.context_check.reason}

### Details

"""
        # Add context details
        for key, value in result.context_check.details.items():
            if key != "suggestion":
                report += f"- **{key}**: {value}\n"

        report += "\n"

        # Add suggestion
        if "suggestion" in result.context_check.details:
            report += f"""### To Enable Review

{result.context_check.details['suggestion']}

"""

        report += """
### Why This Matters

The AI review gate needs sufficient context to provide accurate, actionable feedback.
Very large or scattered PRs are difficult to review comprehensively and are more
likely to have missed issues.

**Best practices:**
- Keep PRs focused on a single concern
- Limit to <5000 lines and <50 files per PR
- Split large features into multiple incremental PRs

---
*Build will FAIL until the PR is adjusted to meet review requirements.*
*For more information: docs/AI_CODE_REVIEW_GATE.md#context-gate*
"""
        return report

    def _format_error(self, result: ReviewResult) -> str:
        """Format error message."""
        report = f"""## 💥 AI Code Review - ERROR

**An error occurred during the review process.**

**Error:** {result.error_message or "Unknown error"}

### What to Do

This is likely a temporary issue. Please try:

1. **Re-run the workflow** - Click "Re-run jobs" in GitHub Actions
2. **Check API status** - Verify Anthropic API is operational
3. **Contact maintainers** - If issue persists, open an issue

---
*Timestamp: {result.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}*
"""
        return report

    def _format_findings_by_severity(
        self, findings: List[Finding], severity: Severity
    ) -> str:
        """
        Format all findings of a specific severity.

        Args:
            findings: All findings
            severity: Severity level to filter

        Returns:
            Formatted markdown section
        """
        filtered = [f for f in findings if f.severity == severity]
        if not filtered:
            return ""

        # Section header
        if severity == Severity.CRITICAL:
            section = "### 🚨 Critical Issues (Must Fix)\n\n"
        elif severity == Severity.WARNING:
            section = "### ⚠️ Warnings\n\n"
        else:
            section = "### ℹ️ Informational\n\n"

        # Format each finding
        for idx, finding in enumerate(filtered, 1):
            section += self._format_finding(finding, idx)
            section += "\n---\n\n"

        return section

    def _format_finding(self, finding: Finding, index: int) -> str:
        """
        Format a single finding.

        Args:
            finding: Finding to format
            index: Index number for display

        Returns:
            Formatted markdown
        """
        # Header
        severity_emoji = self._get_severity_emoji(finding.severity)
        report = f"#### {severity_emoji} {index}. {finding.title}\n\n"

        # Metadata
        report += f"**File**: `{finding.violation.file_path}:{finding.violation.line_start}`\n"
        report += f"**Rule**: {finding.rule_id}\n"
        report += f"**Category**: {finding.category.value.title()}\n"
        report += f"**Severity**: {finding.severity.value.title()}\n\n"

        # Issue description
        report += f"**Issue:**\n{finding.description}\n\n"

        # Code snippet
        if finding.violation.code_snippet:
            report += f"**Problematic Code:**\n```python\n{finding.violation.code_snippet}\n```\n\n"

        # Explanation
        report += f"**Why This Matters:**\n{finding.explanation}\n\n"

        # Suggested fix
        if finding.suggested_fix:
            report += f"**Suggested Fix:**\n```diff\n{finding.suggested_fix}\n```\n\n"
        elif finding.suggested_code:
            report += f"**Suggested Code:**\n```python\n{finding.suggested_code}\n```\n\n"

        # How to apply
        report += "**How to Apply:**\n"
        report += "1. Review the suggested fix above\n"
        report += f"2. Apply changes manually to `{finding.violation.file_path}`\n"
        report += "3. Verify with tests: `pytest tests/`\n"
        report += "4. Push updated code\n\n"

        # Documentation link
        if finding.documentation_url:
            report += f"📚 **Learn More**: [{finding.documentation_url}]({finding.documentation_url})\n\n"

        return report

    def _get_severity_emoji(self, severity: Severity) -> str:
        """Get emoji for severity level."""
        if severity == Severity.CRITICAL:
            return "🚨"
        elif severity == Severity.WARNING:
            return "⚠️"
        else:
            return "ℹ️"

    def _get_category_emoji(self, category: Category) -> str:
        """Get emoji for category."""
        if category == Category.SAFETY:
            return "🔒"
        elif category == Category.CLARITY:
            return "📖"
        else:
            return "🔧"

    def format_summary_json(self, result: ReviewResult) -> str:
        """
        Format review result as JSON for artifact storage.

        Args:
            result: Review result

        Returns:
            JSON string
        """
        import json

        data = {
            "status": result.status.value,
            "pr_number": result.pr_changes.pr_number,
            "summary": result.summary,
            "findings": [
                {
                    "id": f.id,
                    "rule_id": f.rule_id,
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "title": f.title,
                    "file": f.violation.file_path,
                    "line": f.violation.line_start,
                }
                for f in result.findings
            ],
            "execution_time": result.execution_time,
            "timestamp": result.timestamp.isoformat(),
        }

        return json.dumps(data, indent=2)
