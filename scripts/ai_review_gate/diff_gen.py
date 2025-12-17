"""
Diff Generator - Creates suggested fix diffs for manual application.

IMPORTANT: Never applies diffs automatically. All fixes must be manually reviewed
and applied by developers.
"""

import logging
import difflib
from typing import Optional, List, Dict
from .types import Finding, Violation

logger = logging.getLogger(__name__)


class DiffGenerator:
    """
    Generates unified diff patches for suggested code fixes.

    All diffs are for MANUAL application only - never applied automatically.
    """

    def generate_fix_diff(
        self,
        violation: Violation,
        original_code: str,
        suggested_code: str,
        context_lines: int = 3,
    ) -> str:
        """
        Generate a unified diff for a suggested fix.

        Args:
            violation: The violation being fixed
            original_code: Original code snippet
            suggested_code: Suggested replacement code
            context_lines: Number of context lines around the change

        Returns:
            Unified diff string
        """
        # Split into lines
        original_lines = original_code.splitlines(keepends=True)
        suggested_lines = suggested_code.splitlines(keepends=True)

        # Generate unified diff
        diff = difflib.unified_diff(
            original_lines,
            suggested_lines,
            fromfile=f"a/{violation.file_path}",
            tofile=f"b/{violation.file_path}",
            lineterm="",
            n=context_lines,
        )

        diff_text = "\n".join(diff)
        return diff_text

    def generate_inline_suggestion(
        self, violation: Violation, suggested_code: str
    ) -> str:
        """
        Generate an inline code suggestion.

        Args:
            violation: The violation being addressed
            suggested_code: Suggested replacement code

        Returns:
            Formatted suggestion
        """
        suggestion = f"""**Suggested fix for {violation.file_path}:{violation.line_start}**

Replace:
```python
{violation.code_snippet}
```

With:
```python
{suggested_code}
```
"""
        return suggestion

    def generate_fix_for_violation(
        self, violation: Violation, rule_id: str, code_context: str
    ) -> Optional[str]:
        """
        Generate a suggested fix for a specific violation.

        Args:
            violation: The violation to fix
            rule_id: ID of the rule that was violated
            code_context: Full code context around the violation

        Returns:
            Suggested fix code or None if no fix available
        """
        # Pattern-based fixes for common security issues
        if rule_id == "SEC001":  # SQL Injection
            return self._fix_sql_injection(violation, code_context)
        elif rule_id == "SEC002":  # Hardcoded credentials
            return self._fix_hardcoded_credentials(violation)
        elif rule_id == "SEC003":  # Command injection
            return self._fix_command_injection(violation, code_context)
        elif rule_id == "MNT004":  # Missing error handling
            return self._add_error_handling(violation, code_context)

        # For other violations, rely on LLM-generated suggestions
        return None

    def _fix_sql_injection(self, violation: Violation, code_context: str) -> str:
        """Generate fix for SQL injection vulnerability."""
        # Example: convert string concatenation to parameterized query
        original = violation.code_snippet

        # Detect query method
        if "execute" in original:
            fix = original.replace(
                'f"SELECT', '"SELECT'
            )  # Remove f-string
            fix = fix.replace("{", "?").replace("}", "")
            suggestion = f"{fix}\n    # Pass parameters separately: db.execute(query, (param1, param2))"
        else:
            suggestion = "# Use parameterized queries with ? placeholders\n" + original

        return suggestion

    def _fix_hardcoded_credentials(self, violation: Violation) -> str:
        """Generate fix for hardcoded credentials."""
        original = violation.code_snippet

        # Extract variable name
        import re

        match = re.match(r"(\w+)\s*=\s*[\"'][^\"']+[\"']", original)
        if match:
            var_name = match.group(1)
            suggestion = f'{var_name} = os.environ.get("{var_name.upper()}")'
        else:
            suggestion = "# Load from environment variables\nimport os\nvalue = os.environ.get('SECRET_NAME')"

        return suggestion

    def _fix_command_injection(self, violation: Violation, code_context: str) -> str:
        """Generate fix for command injection."""
        original = violation.code_snippet

        # Suggest using list form instead of string
        if "subprocess" in original:
            suggestion = (
                "# Use list form to avoid shell injection\n"
                "# subprocess.run(['command', arg1, arg2], check=True, capture_output=True)"
            )
        else:
            suggestion = (
                "# Avoid os.system() - use subprocess with list arguments instead\n"
                + original
            )

        return suggestion

    def _add_error_handling(self, violation: Violation, code_context: str) -> str:
        """Add error handling around risky operation."""
        original = violation.code_snippet
        indent = " " * (len(original) - len(original.lstrip()))

        suggestion = f"""try:
{indent}    {original.strip()}
{indent}except Exception as e:
{indent}    logger.error(f"Operation failed: {{e}}")
{indent}    raise"""

        return suggestion

    def format_diff_for_display(self, diff: str) -> str:
        """
        Format diff with syntax highlighting markers for display.

        Args:
            diff: Raw unified diff

        Returns:
            Formatted diff for markdown/HTML display
        """
        lines = diff.split("\n")
        formatted = []

        for line in lines:
            if line.startswith("+++") or line.startswith("---"):
                formatted.append(f"**{line}**")
            elif line.startswith("+"):
                formatted.append(f"<span style='color: green;'>{line}</span>")
            elif line.startswith("-"):
                formatted.append(f"<span style='color: red;'>{line}</span>")
            elif line.startswith("@@"):
                formatted.append(f"<span style='color: cyan;'>{line}</span>")
            else:
                formatted.append(line)

        return "\n".join(formatted)

    def create_patch_file(self, findings: List[Finding], output_path: str) -> None:
        """
        Create a .patch file with all suggested fixes.

        Args:
            findings: List of findings with suggested fixes
            output_path: Path to write patch file
        """
        patches = []

        for finding in findings:
            if finding.suggested_fix:
                patches.append(finding.suggested_fix)
                patches.append("")  # Blank line between patches

        if patches:
            with open(output_path, "w") as f:
                f.write("\n".join(patches))

            logger.info(f"Created patch file: {output_path}")
        else:
            logger.info("No patches to write")

    def validate_diff(self, diff: str) -> bool:
        """
        Validate that a diff is well-formed.

        Args:
            diff: Diff to validate

        Returns:
            True if diff is valid
        """
        if not diff:
            return False

        lines = diff.split("\n")

        # Check for required headers
        has_from = any(line.startswith("---") for line in lines)
        has_to = any(line.startswith("+++") for line in lines)
        has_hunk = any(line.startswith("@@") for line in lines)

        return has_from and has_to and has_hunk
