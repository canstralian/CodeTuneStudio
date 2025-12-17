"""
Context Gate - Determines if there's sufficient context for meaningful code review.

Explicitly refuses review when context is insufficient, following the principle:
"No auto-magic. No silent edits. No vibes."
"""

import logging
from typing import Dict, List
from .types import PRChanges, ContextCheck

logger = logging.getLogger(__name__)


class ContextGate:
    """
    Evaluates whether PR changes provide sufficient context for review.

    Refuses review when:
    - Changes are too large
    - Files are too scattered
    - Critical context is missing
    - Binary or generated code without source
    """

    def __init__(
        self,
        max_files: int = 50,
        max_lines: int = 5000,
        max_complexity_score: float = 100.0,
    ):
        """
        Initialize context gate with thresholds.

        Args:
            max_files: Maximum number of files in PR
            max_lines: Maximum total lines changed
            max_complexity_score: Maximum complexity score for changes
        """
        self.max_files = max_files
        self.max_lines = max_lines
        self.max_complexity_score = max_complexity_score

    def check_context_sufficiency(self, changes: PRChanges) -> ContextCheck:
        """
        Determine if context is sufficient for review.

        Args:
            changes: PR changes to evaluate

        Returns:
            ContextCheck with sufficiency determination and reason
        """
        logger.info(f"Checking context sufficiency for PR #{changes.pr_number}")

        # Check 1: File count
        if changes.file_count > self.max_files:
            return ContextCheck(
                is_sufficient=False,
                reason=f"Too many files changed ({changes.file_count} > {self.max_files})",
                details={
                    "file_count": changes.file_count,
                    "threshold": self.max_files,
                    "suggestion": "Split into multiple focused PRs",
                },
            )

        # Check 2: Total lines changed
        if changes.total_changes > self.max_lines:
            return ContextCheck(
                is_sufficient=False,
                reason=f"Too many lines changed ({changes.total_changes} > {self.max_lines})",
                details={
                    "lines_changed": changes.total_changes,
                    "threshold": self.max_lines,
                    "suggestion": "Split into smaller, incremental changes",
                },
            )

        # Check 3: Binary or generated files
        binary_files = self._detect_binary_files(changes)
        if binary_files:
            return ContextCheck(
                is_sufficient=False,
                reason=f"Binary or generated files detected without source context",
                details={
                    "binary_files": binary_files,
                    "suggestion": "Exclude generated files or provide source files",
                },
            )

        # Check 4: Missing patches (truncated diffs)
        missing_patches = self._check_missing_patches(changes)
        if missing_patches:
            return ContextCheck(
                is_sufficient=False,
                reason="Incomplete diff data (GitHub API truncation)",
                details={
                    "files_without_patches": missing_patches,
                    "suggestion": "Review may require local checkout for full context",
                },
            )

        # Check 5: Scattered changes (low cohesion)
        cohesion_score = self._calculate_cohesion(changes)
        if cohesion_score < 0.3:  # Low cohesion threshold
            return ContextCheck(
                is_sufficient=False,
                reason="Changes are too scattered across unrelated areas",
                details={
                    "cohesion_score": cohesion_score,
                    "suggestion": "Group related changes into separate PRs",
                },
            )

        # Check 6: Complexity analysis
        complexity_score = self._calculate_complexity(changes)
        if complexity_score > self.max_complexity_score:
            return ContextCheck(
                is_sufficient=False,
                reason=f"Changes are too complex for automated review ({complexity_score:.1f} > {self.max_complexity_score})",
                details={
                    "complexity_score": complexity_score,
                    "threshold": self.max_complexity_score,
                    "suggestion": "Simplify changes or request manual review",
                },
            )

        # All checks passed
        logger.info("Context is sufficient for review")
        return ContextCheck(
            is_sufficient=True,
            details={
                "file_count": changes.file_count,
                "lines_changed": changes.total_changes,
                "cohesion_score": cohesion_score,
                "complexity_score": complexity_score,
            },
        )

    def _detect_binary_files(self, changes: PRChanges) -> List[str]:
        """
        Detect binary or generated files without source context.

        Returns:
            List of binary/generated file paths
        """
        binary_extensions = {
            ".pyc",
            ".so",
            ".dll",
            ".exe",
            ".bin",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
        }

        generated_patterns = [
            "generated",
            "dist/",
            "build/",
            "node_modules/",
            ".min.js",
            ".min.css",
            "package-lock.json",
            "poetry.lock",
            "Pipfile.lock",
        ]

        binary_files = []

        for file_change in changes.files:
            filename = file_change.filename.lower()

            # Check for binary extensions
            if any(filename.endswith(ext) for ext in binary_extensions):
                binary_files.append(file_change.filename)
                continue

            # Check for generated patterns
            if any(pattern in filename for pattern in generated_patterns):
                binary_files.append(file_change.filename)
                continue

        return binary_files

    def _check_missing_patches(self, changes: PRChanges) -> List[str]:
        """
        Check for files with missing patch data (GitHub API truncation).

        Returns:
            List of files without patches
        """
        missing = []

        for file_change in changes.files:
            # Skip removed files (no patch expected)
            if file_change.status == "removed":
                continue

            # Check if patch is missing when expected
            if file_change.changes > 0 and not file_change.patch:
                missing.append(file_change.filename)

        return missing

    def _calculate_cohesion(self, changes: PRChanges) -> float:
        """
        Calculate cohesion score (0-1) based on file paths.

        Higher score = more related files (same directory/module).
        Lower score = scattered changes across unrelated areas.

        Returns:
            Cohesion score between 0 and 1
        """
        if len(changes.files) <= 1:
            return 1.0  # Single file is perfectly cohesive

        # Extract directory paths
        directories = set()
        for file_change in changes.files:
            parts = file_change.filename.split("/")
            if len(parts) > 1:
                # Get directory path (exclude filename)
                directories.add("/".join(parts[:-1]))
            else:
                directories.add("")  # Root directory

        # Calculate cohesion: fewer unique directories = higher cohesion
        # Formula: 1 - (unique_dirs - 1) / total_files
        cohesion = 1.0 - (len(directories) - 1) / len(changes.files)
        return max(0.0, min(1.0, cohesion))

    def _calculate_complexity(self, changes: PRChanges) -> float:
        """
        Calculate complexity score based on various factors.

        Factors:
        - Number of files
        - Lines changed per file
        - Mix of additions vs deletions
        - File type diversity

        Returns:
            Complexity score (higher = more complex)
        """
        score = 0.0

        # Factor 1: File count (each file adds base complexity)
        score += changes.file_count * 2

        # Factor 2: Lines changed (normalized)
        score += changes.total_changes / 100

        # Factor 3: Additions vs deletions ratio
        # Pure additions or pure deletions are simpler
        # Mixed changes are more complex
        if changes.total_changes > 0:
            add_ratio = changes.total_additions / changes.total_changes
            del_ratio = changes.total_deletions / changes.total_changes
            mix_penalty = min(add_ratio, del_ratio) * 20
            score += mix_penalty

        # Factor 4: File type diversity
        extensions = set()
        for file_change in changes.files:
            if "." in file_change.filename:
                ext = file_change.filename.rsplit(".", 1)[1]
                extensions.add(ext)

        # More diverse file types = more complex
        score += len(extensions) * 5

        return score

    def generate_refusal_message(self, check: ContextCheck) -> str:
        """
        Generate explicit refusal message with actionable guidance.

        Args:
            check: Failed context check

        Returns:
            Formatted refusal message
        """
        message = f"""⛔ **INSUFFICIENT CONTEXT FOR REVIEW**

**This PR cannot be reviewed due to:** {check.reason}

"""

        # Add specific details
        if check.details:
            message += "**Details:**\n"
            for key, value in check.details.items():
                if key == "suggestion":
                    continue  # Handle separately
                message += f"- {key}: {value}\n"

            message += "\n"

        # Add suggestion
        if "suggestion" in check.details:
            message += f"""**To enable review:**
{check.details['suggestion']}

"""

        # Add footer
        message += """**The build will FAIL until these issues are addressed.**

For more information, see: docs/AI_CODE_REVIEW_GATE.md#context-gate
"""

        return message
