# CodeTuneStudio Examples

This directory contains reference implementations demonstrating CodeTuneStudio's capabilities as a senior optimization and refactoring architect.

## 📁 Directory Structure

```
examples/
├── README.md                   # This file
├── GETTING_STARTED.md         # Detailed usage guide
├── run_refactoring_demo.py    # Interactive demonstration
└── refactoring/
    ├── before/                # Code BEFORE refactoring
    │   └── inefficient_code.py
    ├── after/                 # Code AFTER refactoring
    │   └── efficient_code.py
    └── logs/                  # Generated reports
        ├── refactoring_report.txt
        └── refactoring.diff
```

## 🚀 Quick Start

Run the complete demonstration:

```bash
python examples/run_refactoring_demo.py
```

**Output:**
- Analyzes real code with 14+ issues
- Generates structured refactoring plan
- Shows dry-run execution results
- Creates comprehensive report
- Demonstrates negative capability

## 🔄 The Workflow

```
┌─────────────────┐
│   Input Code    │
│  (Python file)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ANALYSIS      │──┐
│  - Performance  │  │ Uses Python AST
│  - Documentation│  │ Static analysis
│  - Type Safety  │  │ Pattern detection
│  - Errors       │  │
└────────┬────────┘  │
         │           │
         ▼           │
┌─────────────────┐  │
│   PLANNING      │  │
│  - Issues found │  │
│  - Confidence   │  │
│  - Safety check │  │
│  - Refusal?     │  │
└────────┬────────┘  │
         │           │
         ▼           │
┌─────────────────┐  │
│   EXECUTION     │  │
│  - Dry run      │  │
│  - Validation   │  │
│  - Apply fixes  │  │
└────────┬────────┘  │
         │           │
         ▼           │
┌─────────────────┐  │
│   CHANGELOG     │◄─┘
│  - Report       │
│  - Diff         │
│  - Audit trail  │
└─────────────────┘
```

## 📊 What Gets Analyzed

### Performance Issues
- String concatenation in loops (O(n²))
- Nested loops (potential O(n²))
- Multiple passes over data
- Inefficient algorithms

### Documentation
- Missing docstrings
- Incomplete documentation
- No type hints

### Type Safety
- Missing type annotations
- Inconsistent types
- No return type hints

### Error Handling
- Bare except clauses
- No error handling
- Poor exception management

### Code Quality
- Public mutable state
- Poor encapsulation
- No input validation

## 📝 Example Output

```
================================================================================
CODETUNESTUDIO REFACTORING REPORT
================================================================================
File: examples/refactoring/before/inefficient_code.py
Timestamp: 2025-12-13T07:34:24
Estimated Complexity: HIGH
Safe to Apply: NO

Issues Found: 14

## PERFORMANCE
--------------------------------------------------------------------------------
1. Line 18 [HIGH]
   Description: String concatenation in loop
   Confidence: high
   Rationale: String concatenation in loops is O(n²). Use list append + join.

[... more issues ...]

## NEGATIVE CAPABILITY DEMONSTRATION
Testing with syntactically invalid code...
✓ Agent correctly REFUSED to refactor invalid code
  Reason: Code has syntax errors: invalid syntax
```

## 🎯 Key Features Demonstrated

### 1. Deterministic Analysis
- Same input always produces same output
- Reproducible results
- No randomness or unpredictability

### 2. Confidence Levels
- **High**: Safe to apply automatically
- **Medium**: Requires review
- **Low**: Suggest only
- **Refuse**: Cannot proceed safely

### 3. Safety Assessment
- Syntax validation before/after
- Complexity estimation
- Auto-apply recommendations
- Full rollback on errors

### 4. Negative Capability
- Explicit refusal when unsafe
- Clear reasons for refusal
- Demonstrates boundaries
- Builds trust through predictability

### 5. Comprehensive Audit Trail
- Detailed issue descriptions
- Rationales for each change
- Before/after comparisons
- Complete diffs

## 🔧 Using in Your Project

### Basic Usage

```python
from core import RefactoringAgent

# Initialize
agent = RefactoringAgent()

# Analyze
code = open('your_code.py').read()
plan = agent.analyze_code(code)

# Check results
if plan.should_refuse():
    print(f"Cannot refactor: {plan.refusal_reason}")
else:
    print(f"Found {len(plan.issues)} issues")
    
    # Generate report
    report = agent.generate_report(plan)
    print(report)
```

### In CI/CD Pipeline

```bash
# Fail build on critical issues
python -c "
from core import RefactoringAgent
import sys

agent = RefactoringAgent()
code = open('src/main.py').read()
plan = agent.analyze_code(code)

critical = [i for i in plan.issues if i.severity == 'critical']
if critical:
    print(f'FAIL: {len(critical)} critical issues')
    sys.exit(1)
"
```

## 📚 Learn More

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Detailed usage guide
- **[REFERENCE_IMPLEMENTATION.md](../REFERENCE_IMPLEMENTATION.md)** - Full documentation
- **[ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - System architecture

## 🧪 Running Tests

```bash
# Test the refactoring agent
python -m unittest tests.test_refactoring_agent -v

# Test the example code
python -m unittest tests.test_refactoring_agent.TestExampleCode -v
```

## 🤝 Contributing

Found a pattern we should detect? Want to add support for another language?

1. Add analysis logic to `core/refactoring_agent.py`
2. Add test cases to `tests/test_refactoring_agent.py`
3. Update documentation
4. Submit a pull request

## 📈 Metrics from Demo

When you run the demo, you'll see:

- **Analysis Time**: < 1ms for typical files
- **Issues Detected**: Performance, docs, types, errors
- **Confidence Distribution**: High/medium/low breakdown
- **Safety Assessment**: Can auto-apply or needs review
- **Report Size**: Comprehensive but readable

## 🎓 Design Philosophy

### Invariants (Never Compromised)

1. **No Logic Changes**: Unless fixing bugs
2. **Full Justification**: Every change explained
3. **Syntax Validation**: Code must parse
4. **Refusal Capability**: Refuse when unsure
5. **Audit Trail**: Complete documentation

### Trade-offs

- **Conservatism > Aggressiveness**: Refuse when unsure
- **Explainability > Cleverness**: Clear rationales
- **Reproducibility > Flexibility**: Deterministic
- **Safety > Speed**: Validation is essential

---

## 💡 The Big Picture

This reference implementation transforms CodeTuneStudio from:

❌ **"An AI that edits code"** (vague, unpredictable)

✅ **"A deterministic lens through which code is allowed to change"** (trusted, reliable)

It proves that:
- The doctrine survives contact with real code
- Negative capability builds trust
- Structured workflows enable predictability
- Documentation creates understanding

---

*"When you're ready, the next evolution is not more features—it's embodiment."*

**This is that embodiment.**
