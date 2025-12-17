"""
Type definitions for the AI Code Review Gate.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class Severity(str, Enum):
    """Severity levels for findings."""

    CRITICAL = "critical"  # Always fails build
    WARNING = "warning"  # Fails in strict mode
    INFO = "info"  # Informational only


class Category(str, Enum):
    """Categories of code issues."""

    SAFETY = "safety"  # Security vulnerabilities
    CLARITY = "clarity"  # Code readability
    MAINTAINABILITY = "maintainability"  # Long-term maintenance


class ReviewStatus(str, Enum):
    """Overall status of the review."""

    PASSED = "passed"  # No issues found
    FAILED = "failed"  # Critical issues found
    REFUSED = "refused"  # Insufficient context
    ERROR = "error"  # System error


@dataclass
class FileChange:
    """Represents a changed file in the PR."""

    filename: str
    status: str  # added, modified, removed, renamed
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None  # Unified diff
    previous_filename: Optional[str] = None  # For renames
    raw_url: Optional[str] = None


@dataclass
class PRChanges:
    """Represents all changes in a pull request."""

    pr_number: int
    title: str
    description: str
    base_ref: str
    head_ref: str
    base_sha: str
    head_sha: str
    files: List[FileChange]
    total_additions: int
    total_deletions: int
    total_changes: int
    file_count: int
    author: str
    created_at: datetime
    updated_at: datetime


@dataclass
class ContextCheck:
    """Result of context sufficiency check."""

    is_sufficient: bool
    reason: Optional[str] = None  # Reason for insufficiency
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Violation:
    """Represents a specific rule violation."""

    rule_id: str
    file_path: str
    line_start: int
    line_end: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None
    message: str
    code_snippet: Optional[str] = None


@dataclass
class Finding:
    """Represents a code review finding."""

    id: str  # Unique finding ID
    rule_id: str
    category: Category
    severity: Severity
    title: str
    description: str  # What's wrong
    explanation: str  # Why it matters
    violation: Violation
    suggested_fix: Optional[str] = None  # Diff patch
    suggested_code: Optional[str] = None  # Replacement code
    documentation_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewResult:
    """Complete result of the code review."""

    status: ReviewStatus
    pr_changes: PRChanges
    findings: List[Finding]
    context_check: ContextCheck
    summary: Dict[str, int] = field(default_factory=dict)  # Stats
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None

    def __post_init__(self):
        """Calculate summary statistics."""
        if not self.summary:
            self.summary = {
                "total_findings": len(self.findings),
                "critical": sum(1 for f in self.findings if f.severity == Severity.CRITICAL),
                "warnings": sum(1 for f in self.findings if f.severity == Severity.WARNING),
                "info": sum(1 for f in self.findings if f.severity == Severity.INFO),
                "files_reviewed": len(set(f.violation.file_path for f in self.findings)),
            }

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return self.summary.get("critical", 0) > 0

    @property
    def exit_code(self) -> int:
        """Determine appropriate exit code."""
        if self.status == ReviewStatus.PASSED:
            return 0
        elif self.status == ReviewStatus.FAILED:
            return 1
        elif self.status == ReviewStatus.REFUSED:
            return 2
        else:  # ERROR
            return 3


@dataclass
class Rule:
    """Defines a review rule."""

    id: str
    category: Category
    severity: Severity
    name: str
    description: str
    pattern: Optional[str] = None  # Regex or AST pattern
    llm_prompt: Optional[str] = None  # For AI-based detection
    documentation_url: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def check(self, code: str, context: Dict[str, Any]) -> Optional[Violation]:
        """
        Check if this rule is violated.

        Must be implemented by specific rule implementations.
        """
        raise NotImplementedError("Rule check must be implemented")


@dataclass
class LLMAnalysis:
    """Result from LLM analysis."""

    findings: List[Dict[str, Any]]
    confidence: float  # 0-1 confidence score
    reasoning: str
    token_usage: Dict[str, int]
    latency: float  # Seconds
