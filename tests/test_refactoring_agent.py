"""
Tests for the RefactoringAgent

These tests validate the core functionality of the refactoring agent,
ensuring it correctly identifies issues, creates plans, and handles
edge cases appropriately.
"""
import unittest
from pathlib import Path

from core.refactoring_agent import (
    ConfidenceLevel,
    RefactoringAgent,
    RefactoringType,
)


class TestRefactoringAgent(unittest.TestCase):
    """Test cases for RefactoringAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = RefactoringAgent()
    
    def test_initialization(self):
        """Test agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertIsInstance(self.agent.analysis_cache, dict)
    
    def test_analyze_valid_code(self):
        """Test analysis of valid Python code."""
        code = """
def test_function():
    return 42
"""
        plan = self.agent.analyze_code(code, Path("test.py"))
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan.file_path, Path("test.py"))
        self.assertIsNone(plan.refusal_reason)
        self.assertFalse(plan.should_refuse())
    
    def test_detect_syntax_error(self):
        """Test that agent refuses code with syntax errors."""
        code = """
def broken_function(
    print("Missing closing paren"
"""
        plan = self.agent.analyze_code(code, Path("broken.py"))
        
        self.assertTrue(plan.should_refuse())
        self.assertIsNotNone(plan.refusal_reason)
        self.assertIn("syntax", plan.refusal_reason.lower())
    
    def test_detect_missing_docstring(self):
        """Test detection of missing docstrings."""
        code = """
def undocumented_function():
    return 42

class UndocumentedClass:
    pass
"""
        plan = self.agent.analyze_code(code)
        
        doc_issues = [
            issue for issue in plan.issues
            if issue.issue_type == RefactoringType.DOCUMENTATION
        ]
        
        # Should find missing docstrings for both function and class
        self.assertGreaterEqual(len(doc_issues), 2)
    
    def test_detect_string_concatenation_in_loop(self):
        """Test detection of inefficient string concatenation."""
        code = """
def inefficient():
    result = ""
    for i in range(10):
        result = result + str(i)
    return result
"""
        plan = self.agent.analyze_code(code)
        
        perf_issues = [
            issue for issue in plan.issues
            if issue.issue_type == RefactoringType.PERFORMANCE
        ]
        
        self.assertGreater(len(perf_issues), 0)
        
        # Check that we found the string concatenation issue
        concat_issues = [
            issue for issue in perf_issues
            if "string concatenation" in issue.description.lower()
        ]
        self.assertGreater(len(concat_issues), 0)
    
    def test_detect_nested_loops(self):
        """Test detection of nested loops."""
        code = """
def nested_loops(data):
    for i in data:
        for j in data:
            if i == j:
                pass
"""
        plan = self.agent.analyze_code(code)
        
        perf_issues = [
            issue for issue in plan.issues
            if issue.issue_type == RefactoringType.PERFORMANCE
        ]
        
        # Should detect nested loop
        nested_issues = [
            issue for issue in perf_issues
            if "nested" in issue.description.lower()
        ]
        self.assertGreater(len(nested_issues), 0)
    
    def test_detect_missing_type_hints(self):
        """Test detection of missing type hints."""
        code = """
def no_hints(x, y):
    return x + y
"""
        plan = self.agent.analyze_code(code)
        
        type_issues = [
            issue for issue in plan.issues
            if issue.issue_type == RefactoringType.TYPE_SAFETY
        ]
        
        self.assertGreater(len(type_issues), 0)
    
    def test_execute_plan_dry_run(self):
        """Test executing a plan in dry-run mode."""
        code = """
def simple():
    return 42
"""
        plan = self.agent.analyze_code(code)
        result = self.agent.execute_plan(code, plan, dry_run=True)
        
        self.assertTrue(result.success)
        self.assertEqual(result.original_code, code)
        self.assertIsNotNone(result.changes_applied)
    
    def test_execute_plan_with_refusal(self):
        """Test that execution fails when plan should be refused."""
        code = "def broken("
        plan = self.agent.analyze_code(code)
        result = self.agent.execute_plan(code, plan)
        
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
    
    def test_generate_report(self):
        """Test report generation."""
        code = """
def test():
    result = ""
    for i in range(5):
        result = result + str(i)
    return result
"""
        plan = self.agent.analyze_code(code, Path("test.py"))
        report = self.agent.generate_report(plan)
        
        self.assertIsInstance(report, str)
        self.assertIn("CODETUNESTUDIO", report)
        self.assertIn("test.py", report)
        self.assertGreater(len(report), 100)
    
    def test_generate_report_with_refusal(self):
        """Test report generation for refused refactoring."""
        code = "def broken("
        plan = self.agent.analyze_code(code, Path("broken.py"))
        report = self.agent.generate_report(plan)
        
        self.assertIn("REFUSED", report)
        self.assertIn(plan.refusal_reason, report)
    
    def test_generate_diff(self):
        """Test diff generation."""
        original = "def old():\n    return 1\n"
        refactored = "def new():\n    return 2\n"
        
        diff = self.agent.generate_diff(original, refactored, "test.py")
        
        self.assertIsInstance(diff, str)
        self.assertIn("test.py", diff)
        self.assertIn("-", diff)  # Deletions
        self.assertIn("+", diff)  # Additions
    
    def test_safety_assessment_all_high_confidence(self):
        """Test safety assessment with all high-confidence issues."""
        code = """
def undocumented():
    pass
"""
        plan = self.agent.analyze_code(code)
        
        # Documentation issues are typically high confidence
        if plan.issues:
            high_conf_count = sum(
                1 for issue in plan.issues
                if issue.confidence == ConfidenceLevel.HIGH
            )
            self.assertGreater(high_conf_count, 0)
    
    def test_complexity_assessment(self):
        """Test complexity assessment based on issue count."""
        # Simple code with few issues
        simple_code = """
def simple():
    return 42
"""
        simple_plan = self.agent.analyze_code(simple_code)
        self.assertEqual(simple_plan.estimated_complexity, "low")
    
    def test_confidence_levels(self):
        """Test that issues have appropriate confidence levels."""
        code = """
def test():
    result = ""
    for i in range(5):
        result += str(i)
"""
        plan = self.agent.analyze_code(code)
        
        # All issues should have a confidence level
        for issue in plan.issues:
            self.assertIsInstance(issue.confidence, ConfidenceLevel)
    
    def test_issue_severity(self):
        """Test that issues have appropriate severity."""
        code = """
def test():
    try:
        pass
    except:
        pass
"""
        plan = self.agent.analyze_code(code)
        
        # Bare except should be high severity
        error_handling_issues = [
            issue for issue in plan.issues
            if issue.issue_type == RefactoringType.ERROR_HANDLING
        ]
        
        if error_handling_issues:
            self.assertEqual(error_handling_issues[0].severity, "high")


class TestRefactoringPlan(unittest.TestCase):
    """Test RefactoringPlan functionality."""
    
    def test_add_issue(self):
        """Test adding issues to a plan."""
        from core.refactoring_agent import RefactoringPlan, RefactoringIssue
        
        plan = RefactoringPlan(file_path=Path("test.py"))
        issue = RefactoringIssue(
            issue_type=RefactoringType.PERFORMANCE,
            line_number=10,
            severity="high",
            description="Test issue",
            current_code="test code"
        )
        
        plan.add_issue(issue)
        self.assertEqual(len(plan.issues), 1)
        self.assertEqual(plan.issues[0], issue)


class TestExampleCode(unittest.TestCase):
    """Test the reference implementation example code."""
    
    def test_before_code_has_issues(self):
        """Test that the 'before' example code has issues."""
        from pathlib import Path
        
        examples_dir = Path(__file__).parent.parent / "examples"
        before_file = examples_dir / "refactoring" / "before" / "inefficient_code.py"
        
        if not before_file.exists():
            self.skipTest("Example code not found")
        
        with open(before_file, 'r') as f:
            code = f.read()
        
        agent = RefactoringAgent()
        plan = agent.analyze_code(code, before_file)
        
        # The before code should have multiple issues
        self.assertGreater(len(plan.issues), 5)
        
        # Should have performance issues
        perf_issues = [
            issue for issue in plan.issues
            if issue.issue_type == RefactoringType.PERFORMANCE
        ]
        self.assertGreater(len(perf_issues), 0)
    
    def test_after_code_syntax_valid(self):
        """Test that the 'after' example code is syntactically valid."""
        from pathlib import Path
        import ast
        
        examples_dir = Path(__file__).parent.parent / "examples"
        after_file = examples_dir / "refactoring" / "after" / "efficient_code.py"
        
        if not after_file.exists():
            self.skipTest("Example code not found")
        
        with open(after_file, 'r') as f:
            code = f.read()
        
        # Should parse without errors
        try:
            ast.parse(code)
        except SyntaxError:
            self.fail("After code has syntax errors")


if __name__ == "__main__":
    unittest.main()
