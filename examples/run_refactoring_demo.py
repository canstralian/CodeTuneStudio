#!/usr/bin/env python3
"""
CodeTuneStudio Reference Implementation Demo

This script demonstrates the complete workflow of the refactoring agent:
1. Analysis - Examine code and identify issues
2. Planning - Create a structured refactoring plan
3. Execution - Apply transformations (in this demo, manual)
4. Changelog - Document all changes made

This is the "minimal, runnable instance" that proves the doctrine
survives contact with real, ugly code.
"""
import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.refactoring_agent import RefactoringAgent


def run_demo():
    """Run the complete refactoring demonstration."""
    
    print("=" * 80)
    print("CodeTuneStudio - Reference Implementation Demo")
    print("=" * 80)
    print()
    print("This demonstration shows:")
    print("  1. Analysis → Plan → Execution → Changelog workflow")
    print("  2. Identification of performance, documentation, and safety issues")
    print("  3. Negative capability (deliberate refusal when appropriate)")
    print("  4. Deterministic, reproducible refactoring")
    print()
    print("=" * 80)
    print()
    
    # Load the example code
    examples_dir = Path(__file__).parent
    before_file = examples_dir / "refactoring" / "before" / "inefficient_code.py"
    after_file = examples_dir / "refactoring" / "after" / "efficient_code.py"
    
    if not before_file.exists():
        print(f"❌ Error: Could not find {before_file}")
        return 1
    
    print(f"📂 Analyzing: {before_file}")
    print()
    
    # Read the code
    with open(before_file, 'r') as f:
        original_code = f.read()
    
    # Initialize the agent
    agent = RefactoringAgent()
    
    # Step 1: Analysis
    print("🔍 STEP 1: ANALYSIS")
    print("-" * 80)
    plan = agent.analyze_code(original_code, before_file)
    print(f"✓ Analysis complete: {len(plan.issues)} issues identified")
    print()
    
    # Step 2: Planning
    print("📋 STEP 2: PLANNING")
    print("-" * 80)
    print(f"Complexity: {plan.estimated_complexity.upper()}")
    print(f"Safe to auto-apply: {'YES' if plan.safe_to_apply else 'NO'}")
    print(f"Should refuse: {'YES' if plan.should_refuse() else 'NO'}")
    print()
    
    # Step 3: Execution (dry run)
    print("⚙️  STEP 3: EXECUTION (Dry Run)")
    print("-" * 80)
    result = agent.execute_plan(original_code, plan, dry_run=True)
    print(f"✓ Dry run complete in {result.execution_time:.3f}s")
    print()
    
    # Step 4: Generate comprehensive report
    print("📄 STEP 4: CHANGELOG & REPORT")
    print("-" * 80)
    report = agent.generate_report(plan, result)
    print(report)
    print()
    
    # Save the report
    log_dir = examples_dir / "refactoring" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    report_file = log_dir / "refactoring_report.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    print()
    
    # Show the comparison with after code
    if after_file.exists():
        print("=" * 80)
        print("COMPARISON: Before vs After")
        print("=" * 80)
        print()
        print(f"BEFORE: {before_file.name}")
        print(f"  - Lines: {len(original_code.splitlines())}")
        print(f"  - Issues: {len(plan.issues)}")
        print()
        
        with open(after_file, 'r') as f:
            refactored_code = f.read()
        
        print(f"AFTER:  {after_file.name}")
        print(f"  - Lines: {len(refactored_code.splitlines())}")
        print(f"  - Added: Type hints, docstrings, error handling")
        print(f"  - Fixed: Performance issues, encapsulation")
        print()
        
        # Generate diff
        diff = agent.generate_diff(original_code, refactored_code, "inefficient_code.py")
        if diff:
            diff_file = log_dir / "refactoring.diff"
            with open(diff_file, 'w') as f:
                f.write(diff)
            print(f"💾 Diff saved to: {diff_file}")
        print()
    
    # Demonstrate negative capability with bad code
    print("=" * 80)
    print("NEGATIVE CAPABILITY DEMONSTRATION")
    print("=" * 80)
    print()
    print("Testing with syntactically invalid code...")
    print()
    
    bad_code = """
def broken_function(
    # This is intentionally broken
    print("This will cause a syntax error"
"""
    
    bad_plan = agent.analyze_code(bad_code, Path("broken.py"))
    if bad_plan.should_refuse():
        print("✓ Agent correctly REFUSED to refactor invalid code")
        print(f"  Reason: {bad_plan.refusal_reason}")
    else:
        print("✗ Agent should have refused but didn't")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("✅ This demonstration shows:")
    print("   • Deterministic analysis of real code")
    print("   • Structured planning with confidence levels")
    print("   • Safe execution with validation")
    print("   • Comprehensive changelog/audit trail")
    print("   • Negative capability (refusal when appropriate)")
    print()
    print("📚 Next steps:")
    print("   • Review the refactoring report in logs/")
    print("   • Compare before/ and after/ code")
    print("   • Read REFERENCE_IMPLEMENTATION.md for details")
    print()
    print("This is the 'embodiment' - a minimal, runnable instance that proves")
    print("the doctrine survives contact with real, ugly code.")
    print()
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(run_demo())
