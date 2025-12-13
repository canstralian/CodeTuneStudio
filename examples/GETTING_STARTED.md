# Getting Started with CodeTuneStudio Reference Implementation

This guide walks you through using the reference implementation to understand how CodeTuneStudio operates as a "senior optimization and refactoring architect."

## Quick Start (5 minutes)

### 1. Run the Demo

```bash
python examples/run_refactoring_demo.py
```

This will:
- Analyze example code with multiple issues
- Generate a structured refactoring plan
- Execute a dry run showing what would change
- Create comprehensive reports and diffs
- Demonstrate refusal with invalid code

### 2. Review the Results

Check the generated files:

```bash
# View the detailed report
cat examples/refactoring/logs/refactoring_report.txt

# See the diff between before/after
cat examples/refactoring/logs/refactoring.diff
```

### 3. Explore the Code

```bash
# Compare before and after
diff examples/refactoring/before/inefficient_code.py \
     examples/refactoring/after/efficient_code.py
```

## Understanding the Workflow

### Phase 1: Analysis

The agent performs static analysis using Python's AST:

```python
from core import RefactoringAgent

agent = RefactoringAgent()
code = open('my_code.py').read()
plan = agent.analyze_code(code)

print(f"Found {len(plan.issues)} issues")
```

**What it detects:**
- Performance anti-patterns (string concat in loops, O(n²) algorithms)
- Missing documentation (docstrings)
- Type safety (missing type hints)
- Error handling (bare except clauses)

### Phase 2: Planning

The agent creates a structured plan with safety assessment:

```python
for issue in plan.issues:
    print(f"{issue.line_number}: {issue.description}")
    print(f"  Severity: {issue.severity}")
    print(f"  Confidence: {issue.confidence.value}")
    print(f"  Rationale: {issue.rationale}")
```

**Key features:**
- Confidence levels (high/medium/low/refuse)
- Safety assessment (safe to auto-apply?)
- Complexity estimation (low/medium/high)
- Refusal reasons when applicable

### Phase 3: Execution

The agent can execute plans in dry-run or live mode:

```python
# Dry run - see what would happen
result = agent.execute_plan(code, plan, dry_run=True)

# Live execution (future capability)
# result = agent.execute_plan(code, plan, dry_run=False)
```

### Phase 4: Changelog

Generate comprehensive documentation:

```python
# Human-readable report
report = agent.generate_report(plan, result)
print(report)

# Unified diff
diff = agent.generate_diff(original, refactored)
```

## Using the Agent Programmatically

### Basic Usage

```python
from pathlib import Path
from core import RefactoringAgent

# Initialize agent
agent = RefactoringAgent()

# Analyze your code
code = Path("your_code.py").read_text()
plan = agent.analyze_code(code, Path("your_code.py"))

# Check if refactoring should be refused
if plan.should_refuse():
    print(f"Cannot refactor: {plan.refusal_reason}")
else:
    # Generate report
    report = agent.generate_report(plan)
    
    # Save to file
    Path("refactoring_report.txt").write_text(report)
```

### Advanced Usage

```python
# Filter issues by type
from core.refactoring_agent import RefactoringType

perf_issues = [
    issue for issue in plan.issues
    if issue.issue_type == RefactoringType.PERFORMANCE
]

# Filter by confidence
from core.refactoring_agent import ConfidenceLevel

high_confidence = [
    issue for issue in plan.issues
    if issue.confidence == ConfidenceLevel.HIGH
]

# Check safety
if plan.safe_to_apply:
    print("All issues have high confidence - safe to auto-apply")
else:
    print("Manual review required")
```

## Examples of What Gets Detected

### 1. Performance Issues

**Before:**
```python
def process(items):
    result = ""
    for item in items:
        result = result + str(item)  # O(n²) string concatenation
    return result
```

**After:**
```python
def process(items: List[str]) -> str:
    """Process items efficiently."""
    return "".join(str(item) for item in items)  # O(n) with join
```

### 2. Missing Documentation

**Before:**
```python
def calculate(x, y):
    return x * y + 10
```

**After:**
```python
def calculate(x: float, y: float) -> float:
    """
    Calculate a value using a formula.
    
    Args:
        x: First operand
        y: Second operand
        
    Returns:
        Result of x * y + 10
    """
    return x * y + 10
```

### 3. Error Handling

**Before:**
```python
try:
    risky_operation()
except:  # Catches everything, including SystemExit
    pass
```

**After:**
```python
try:
    risky_operation()
except ValueError as e:  # Specific exception
    logger.error(f"Operation failed: {e}")
    raise
```

## Negative Capability Examples

The agent explicitly refuses when it cannot safely refactor:

### Syntax Errors

```python
bad_code = "def broken("
plan = agent.analyze_code(bad_code)
# plan.should_refuse() == True
# plan.refusal_reason == "Code has syntax errors: ..."
```

### Insufficient Context (Future)

```python
ambiguous = """
def process(x):
    return x + y  # Where does 'y' come from?
"""
plan = agent.analyze_code(ambiguous)
# Would refuse due to undefined variable
```

## Extending the Agent

### Add Custom Analysis Rules

```python
# In core/refactoring_agent.py

def _analyze_custom(self, tree: ast.AST, plan: RefactoringPlan) -> None:
    """Add your custom analysis logic."""
    for node in ast.walk(tree):
        if self._is_custom_issue(node):
            plan.add_issue(RefactoringIssue(
                issue_type=RefactoringType.CUSTOM,
                line_number=node.lineno,
                severity="medium",
                description="Custom issue detected",
                current_code="...",
                rationale="Explain why this matters",
                confidence=ConfidenceLevel.HIGH
            ))
```

### Create a Plugin

```python
from utils.plugins.base import AgentTool, ToolMetadata
from core import RefactoringAgent

class RefactoringPlugin(AgentTool):
    def __init__(self):
        super().__init__()
        self.agent = RefactoringAgent()
        self.metadata = ToolMetadata(
            name="refactoring_tool",
            description="Automated code refactoring",
            version="1.0.0"
        )
    
    def execute(self, inputs: dict) -> dict:
        code = inputs["code"]
        plan = self.agent.analyze_code(code)
        return {
            "issues": len(plan.issues),
            "report": self.agent.generate_report(plan)
        }
```

## Testing Your Changes

```bash
# Run the refactoring agent tests
python -m unittest tests.test_refactoring_agent -v

# Run all tests
python -m unittest discover -s tests

# Test with your own code
python -c "
from pathlib import Path
from core import RefactoringAgent

agent = RefactoringAgent()
code = Path('your_file.py').read_text()
plan = agent.analyze_code(code)
print(agent.generate_report(plan))
"
```

## Next Steps

1. **Read the Full Documentation**: See [REFERENCE_IMPLEMENTATION.md](../REFERENCE_IMPLEMENTATION.md)
2. **Explore the Code**: Check out `core/refactoring_agent.py`
3. **Review Examples**: Look at `examples/refactoring/before/` and `after/`
4. **Run Tests**: `python -m unittest tests.test_refactoring_agent`
5. **Extend the Agent**: Add your own analysis rules

## FAQ

**Q: Can I use this on production code?**
A: The current version is a reference implementation for demonstration. For production use, thoroughly test on your codebase first.

**Q: Does it modify my files automatically?**
A: No. The current implementation runs in dry-run mode by default. It generates reports showing what would change.

**Q: What languages are supported?**
A: Currently Python only. The architecture is designed to be extensible to other languages.

**Q: How do I add support for my coding standards?**
A: Extend the `RefactoringAgent` class and add custom analysis methods. See "Extending the Agent" above.

**Q: Can I integrate this with my CI/CD?**
A: Yes! Run the agent in your CI pipeline and fail builds if critical issues are found:

```bash
python -c "
from core import RefactoringAgent
import sys

agent = RefactoringAgent()
plan = agent.analyze_code(open('code.py').read())

critical = [i for i in plan.issues if i.severity == 'critical']
if critical:
    print(f'Found {len(critical)} critical issues')
    sys.exit(1)
"
```

## Support

- **Documentation**: [REFERENCE_IMPLEMENTATION.md](../REFERENCE_IMPLEMENTATION.md)
- **Architecture**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Issues**: [GitHub Issues](https://github.com/canstralian/CodeTuneStudio/issues)

---

*This reference implementation proves that CodeTuneStudio can operate as a deterministic lens through which code is allowed to change.*
