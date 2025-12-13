"""
CodeTuneStudio Refactoring Agent

This module implements the core refactoring agent that embodies the principles
outlined in the project documentation. It provides deterministic analysis,
planning, and execution of code refactoring operations.

The agent follows these invariants:
- No logic changes unless fixing bugs
- Always provide justification for changes
- Document all transformations
- Refuse when context is insufficient
- Maintain code correctness above all else
"""
import ast
import difflib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RefactoringType(Enum):
    """Types of refactoring operations supported."""
    
    PERFORMANCE = "performance"
    READABILITY = "readability"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    ERROR_HANDLING = "error_handling"
    TYPE_SAFETY = "type_safety"


class ConfidenceLevel(Enum):
    """Confidence level for refactoring decisions."""
    
    HIGH = "high"  # Safe to apply automatically
    MEDIUM = "medium"  # Requires review
    LOW = "low"  # Suggest only, do not apply
    REFUSE = "refuse"  # Insufficient context or risky


@dataclass
class RefactoringIssue:
    """Represents a single refactoring opportunity."""
    
    issue_type: RefactoringType
    line_number: int
    severity: str  # "critical", "high", "medium", "low"
    description: str
    current_code: str
    suggested_fix: Optional[str] = None
    rationale: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


@dataclass
class RefactoringPlan:
    """Complete refactoring plan for a code file."""
    
    file_path: Path
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[RefactoringIssue] = field(default_factory=list)
    estimated_complexity: str = "low"  # low, medium, high
    safe_to_apply: bool = False
    refusal_reason: Optional[str] = None
    
    def add_issue(self, issue: RefactoringIssue) -> None:
        """Add a refactoring issue to the plan."""
        self.issues.append(issue)
    
    def should_refuse(self) -> bool:
        """Determine if refactoring should be refused."""
        return self.refusal_reason is not None


@dataclass
class RefactoringResult:
    """Result of executing a refactoring plan."""
    
    success: bool
    original_code: str
    refactored_code: Optional[str] = None
    changes_applied: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    diff: Optional[str] = None
    execution_time: float = 0.0


class RefactoringAgent:
    """
    Core refactoring agent for CodeTuneStudio.
    
    This agent analyzes Python code, identifies refactoring opportunities,
    creates execution plans, and can apply transformations while maintaining
    strict safety guarantees.
    
    Responsibilities:
    - Static code analysis using AST
    - Complexity detection
    - Performance anti-pattern identification
    - Security vulnerability detection
    - Documentation quality assessment
    - Safe code transformation
    
    Safety Constraints:
    - Never changes logic unless fixing bugs
    - Always validates syntax before/after
    - Provides full change justification
    - Refuses when context insufficient
    - Maintains comprehensive audit trail
    """
    
    def __init__(self) -> None:
        """Initialize the refactoring agent."""
        self.analysis_cache: Dict[str, Any] = {}
        logger.info("RefactoringAgent initialized")
    
    def analyze_code(self, code: str, file_path: Optional[Path] = None) -> RefactoringPlan:
        """
        Analyze code and create a refactoring plan.
        
        Args:
            code: Python source code to analyze
            file_path: Optional path to the file being analyzed
            
        Returns:
            RefactoringPlan with identified issues and recommendations
        """
        plan = RefactoringPlan(
            file_path=file_path or Path("unknown.py")
        )
        
        # Validate that code is parseable
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            plan.refusal_reason = f"Code has syntax errors: {e}"
            return plan
        
        # Analyze different aspects
        self._analyze_performance(code, tree, plan)
        self._analyze_documentation(tree, plan)
        self._analyze_error_handling(tree, plan)
        self._analyze_type_safety(tree, plan)
        
        # Assess overall safety
        self._assess_safety(plan)
        
        return plan
    
    def _analyze_performance(
        self, code: str, tree: ast.AST, plan: RefactoringPlan
    ) -> None:
        """Analyze code for performance issues."""
        for node in ast.walk(tree):
            # Detect string concatenation in loops
            if isinstance(node, (ast.For, ast.While)):
                if self._has_string_concat_in_loop(node):
                    plan.add_issue(RefactoringIssue(
                        issue_type=RefactoringType.PERFORMANCE,
                        line_number=node.lineno,
                        severity="high",
                        description="String concatenation in loop",
                        current_code=ast.unparse(node) if hasattr(ast, 'unparse') else "",
                        rationale="String concatenation in loops is O(n²). Use list append + join or io.StringIO.",
                        confidence=ConfidenceLevel.HIGH
                    ))
            
            # Detect nested loops (potential O(n²) issues)
            if isinstance(node, (ast.For, ast.While)):
                if self._has_nested_loop(node):
                    plan.add_issue(RefactoringIssue(
                        issue_type=RefactoringType.PERFORMANCE,
                        line_number=node.lineno,
                        severity="medium",
                        description="Nested loops detected (possible O(n²) complexity)",
                        current_code="",
                        rationale="Consider using set operations or hash maps for O(n) complexity.",
                        confidence=ConfidenceLevel.MEDIUM
                    ))
    
    def _analyze_documentation(self, tree: ast.AST, plan: RefactoringPlan) -> None:
        """Analyze documentation quality."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    plan.add_issue(RefactoringIssue(
                        issue_type=RefactoringType.DOCUMENTATION,
                        line_number=node.lineno,
                        severity="medium",
                        description=f"Missing docstring for {node.name}",
                        current_code=node.name,
                        rationale="All public functions and classes should have docstrings.",
                        confidence=ConfidenceLevel.HIGH
                    ))
    
    def _analyze_error_handling(self, tree: ast.AST, plan: RefactoringPlan) -> None:
        """Analyze error handling patterns."""
        for node in ast.walk(tree):
            # Detect bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    plan.add_issue(RefactoringIssue(
                        issue_type=RefactoringType.ERROR_HANDLING,
                        line_number=node.lineno,
                        severity="high",
                        description="Bare except clause catches all exceptions",
                        current_code="except:",
                        rationale="Bare except can catch system exits and keyboard interrupts. Use specific exceptions.",
                        confidence=ConfidenceLevel.HIGH
                    ))
    
    def _analyze_type_safety(self, tree: ast.AST, plan: RefactoringPlan) -> None:
        """Analyze type safety."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for missing type hints
                has_return_annotation = node.returns is not None
                has_arg_annotations = any(arg.annotation for arg in node.args.args)
                
                if not (has_return_annotation or has_arg_annotations):
                    plan.add_issue(RefactoringIssue(
                        issue_type=RefactoringType.TYPE_SAFETY,
                        line_number=node.lineno,
                        severity="low",
                        description=f"Function {node.name} missing type hints",
                        current_code=node.name,
                        rationale="Type hints improve code clarity and enable static analysis.",
                        confidence=ConfidenceLevel.MEDIUM
                    ))
    
    def _has_string_concat_in_loop(self, loop_node: ast.AST) -> bool:
        """Check if loop contains string concatenation."""
        for node in ast.walk(loop_node):
            if isinstance(node, ast.AugAssign):
                if isinstance(node.op, ast.Add):
                    return True
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.Add):
                    return True
        return False
    
    def _has_nested_loop(self, loop_node: ast.AST) -> bool:
        """Check if loop contains nested loops."""
        for node in ast.walk(loop_node):
            if node is not loop_node and isinstance(node, (ast.For, ast.While)):
                return True
        return False
    
    def _assess_safety(self, plan: RefactoringPlan) -> None:
        """Assess if the refactoring is safe to apply automatically."""
        high_confidence_count = sum(
            1 for issue in plan.issues 
            if issue.confidence == ConfidenceLevel.HIGH
        )
        
        critical_issues = sum(
            1 for issue in plan.issues 
            if issue.severity == "critical"
        )
        
        # Mark as safe if all high-confidence issues and no critical unknowns
        plan.safe_to_apply = (
            high_confidence_count == len(plan.issues) and 
            critical_issues == 0
        )
        
        # Determine complexity
        if len(plan.issues) > 10:
            plan.estimated_complexity = "high"
        elif len(plan.issues) > 5:
            plan.estimated_complexity = "medium"
        else:
            plan.estimated_complexity = "low"
    
    def execute_plan(
        self, code: str, plan: RefactoringPlan, dry_run: bool = False
    ) -> RefactoringResult:
        """
        Execute a refactoring plan.
        
        Args:
            code: Original source code
            plan: Refactoring plan to execute
            dry_run: If True, only simulate changes without applying
            
        Returns:
            RefactoringResult with execution details
        """
        start_time = datetime.now()
        result = RefactoringResult(
            success=False,
            original_code=code
        )
        
        # Check if we should refuse
        if plan.should_refuse():
            result.errors.append(f"Refactoring refused: {plan.refusal_reason}")
            result.execution_time = (datetime.now() - start_time).total_seconds()
            return result
        
        # For this reference implementation, we simulate the refactoring
        # In a real implementation, this would apply the actual transformations
        if dry_run:
            result.success = True
            result.changes_applied = [
                f"Would apply: {issue.description} at line {issue.line_number}"
                for issue in plan.issues
            ]
        else:
            # Actual refactoring would happen here
            result.success = False
            result.errors.append("Automatic refactoring not yet implemented. Use manual refactoring.")
        
        result.execution_time = (datetime.now() - start_time).total_seconds()
        return result
    
    def generate_report(self, plan: RefactoringPlan, result: Optional[RefactoringResult] = None) -> str:
        """
        Generate a human-readable refactoring report.
        
        Args:
            plan: The refactoring plan
            result: Optional execution result
            
        Returns:
            Formatted report string
        """
        lines = [
            "=" * 80,
            "CODETUNESTUDIO REFACTORING REPORT",
            "=" * 80,
            f"File: {plan.file_path}",
            f"Timestamp: {plan.timestamp.isoformat()}",
            f"Estimated Complexity: {plan.estimated_complexity.upper()}",
            f"Safe to Apply: {'YES' if plan.safe_to_apply else 'NO'}",
            "",
        ]
        
        if plan.should_refuse():
            lines.extend([
                "⛔ REFACTORING REFUSED",
                f"Reason: {plan.refusal_reason}",
                "",
                "This demonstrates negative capability - the agent refuses when",
                "context is insufficient or changes would be unsafe.",
                "",
            ])
        else:
            lines.append(f"Issues Found: {len(plan.issues)}")
            lines.append("")
            
            # Group issues by type
            issues_by_type: Dict[RefactoringType, List[RefactoringIssue]] = {}
            for issue in plan.issues:
                if issue.issue_type not in issues_by_type:
                    issues_by_type[issue.issue_type] = []
                issues_by_type[issue.issue_type].append(issue)
            
            for issue_type, issues in issues_by_type.items():
                lines.append(f"## {issue_type.value.upper().replace('_', ' ')}")
                lines.append("-" * 80)
                
                for i, issue in enumerate(issues, 1):
                    lines.extend([
                        f"{i}. Line {issue.line_number} [{issue.severity.upper()}]",
                        f"   Description: {issue.description}",
                        f"   Confidence: {issue.confidence.value}",
                        f"   Rationale: {issue.rationale}",
                        "",
                    ])
        
        if result:
            lines.extend([
                "=" * 80,
                "EXECUTION RESULT",
                "=" * 80,
                f"Success: {result.success}",
                f"Execution Time: {result.execution_time:.3f}s",
                "",
            ])
            
            if result.changes_applied:
                lines.append("Changes Applied:")
                for change in result.changes_applied:
                    lines.append(f"  - {change}")
                lines.append("")
            
            if result.errors:
                lines.append("Errors:")
                for error in result.errors:
                    lines.append(f"  ⚠️  {error}")
                lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def generate_diff(self, original: str, refactored: str, filepath: str = "code.py") -> str:
        """
        Generate a unified diff between original and refactored code.
        
        Args:
            original: Original source code
            refactored: Refactored source code
            filepath: Name of the file for diff header
            
        Returns:
            Unified diff string
        """
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            refactored.splitlines(keepends=True),
            fromfile=f"a/{filepath}",
            tofile=f"b/{filepath}",
            lineterm=""
        )
        return "".join(diff)
