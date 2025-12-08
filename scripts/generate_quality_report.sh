#!/bin/bash
# Generate Code Quality Report
# This script runs all static analysis tools and generates a comprehensive report

set -e

echo "======================================"
echo "CodeTuneStudio Quality Report Generator"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create reports directory
REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "📊 Running static analysis tools..."
echo ""

# Check if tools are installed
echo "🔍 Checking required tools..."
command -v ruff >/dev/null 2>&1 || { echo -e "${RED}❌ ruff not installed${NC}"; exit 1; }
command -v flake8 >/dev/null 2>&1 || { echo -e "${RED}❌ flake8 not installed${NC}"; exit 1; }
command -v bandit >/dev/null 2>&1 || { echo -e "${RED}❌ bandit not installed${NC}"; exit 1; }
command -v black >/dev/null 2>&1 || { echo -e "${RED}❌ black not installed${NC}"; exit 1; }
echo -e "${GREEN}✅ All required tools installed${NC}"
echo ""

# 1. Ruff Analysis
echo "1️⃣  Running Ruff linter..."
ruff check . --output-format=concise > "$REPORT_DIR/ruff_${TIMESTAMP}.txt" 2>&1 || true
RUFF_COUNT=$(wc -l < "$REPORT_DIR/ruff_${TIMESTAMP}.txt")
echo -e "   ${YELLOW}Found $RUFF_COUNT issues${NC}"

# Generate Ruff statistics
echo "   Generating Ruff statistics..."
ruff check . --output-format=concise 2>&1 | \
    awk -F: '{print $3}' | awk '{print $1}' | \
    sort | uniq -c | sort -rn > "$REPORT_DIR/ruff_stats_${TIMESTAMP}.txt" || true

# 2. Flake8 Analysis
echo "2️⃣  Running Flake8 linter..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics > "$REPORT_DIR/flake8_critical_${TIMESTAMP}.txt" 2>&1 || true
flake8 . --count --exit-zero --max-complexity=18 --max-line-length=88 --statistics > "$REPORT_DIR/flake8_full_${TIMESTAMP}.txt" 2>&1 || true
FLAKE8_CRITICAL=$(grep -c "^" "$REPORT_DIR/flake8_critical_${TIMESTAMP}.txt" || echo "0")
echo -e "   ${GREEN}Critical errors: $FLAKE8_CRITICAL${NC}"

# 3. Bandit Security Analysis
echo "3️⃣  Running Bandit security scanner..."
bandit -r . -f json -o "$REPORT_DIR/bandit_${TIMESTAMP}.json" --exclude "./venv/*,./ENV/*,./env/*,./.venv/*" 2>&1 || true
bandit -r . -f txt -o "$REPORT_DIR/bandit_${TIMESTAMP}.txt" --exclude "./venv/*,./ENV/*,./env/*,./.venv/*" 2>&1 || true

# Extract security summary
if [ -f "$REPORT_DIR/bandit_${TIMESTAMP}.json" ]; then
    BANDIT_HIGH=$(python3 -c "import json; data=json.load(open('$REPORT_DIR/bandit_${TIMESTAMP}.json')); print(sum(1 for r in data.get('results', []) if r['issue_severity']=='HIGH'))" 2>/dev/null || echo "0")
    BANDIT_MEDIUM=$(python3 -c "import json; data=json.load(open('$REPORT_DIR/bandit_${TIMESTAMP}.json')); print(sum(1 for r in data.get('results', []) if r['issue_severity']=='MEDIUM'))" 2>/dev/null || echo "0")
    echo -e "   ${RED}High severity: $BANDIT_HIGH${NC}"
    echo -e "   ${YELLOW}Medium severity: $BANDIT_MEDIUM${NC}"
fi

# 4. Black Formatting Check
echo "4️⃣  Checking code formatting with Black..."
black --check --diff . > "$REPORT_DIR/black_${TIMESTAMP}.txt" 2>&1 || true
BLACK_FILES=$(grep -c "would reformat" "$REPORT_DIR/black_${TIMESTAMP}.txt" 2>/dev/null || echo "0")
if [ "$BLACK_FILES" -eq 0 ]; then
    echo -e "   ${GREEN}✅ All files properly formatted${NC}"
else
    echo -e "   ${YELLOW}⚠️  $BLACK_FILES files need formatting${NC}"
fi

# 5. Test Execution (if pytest available)
if command -v pytest >/dev/null 2>&1; then
    echo "5️⃣  Running tests..."
    pytest tests/ -v --tb=short > "$REPORT_DIR/pytest_${TIMESTAMP}.txt" 2>&1 || true
    TEST_PASSED=$(grep -c "passed" "$REPORT_DIR/pytest_${TIMESTAMP}.txt" 2>/dev/null || echo "0")
    TEST_FAILED=$(grep -c "failed" "$REPORT_DIR/pytest_${TIMESTAMP}.txt" 2>/dev/null || echo "0")
    echo -e "   ${GREEN}Passed: $TEST_PASSED${NC} | ${RED}Failed: $TEST_FAILED${NC}"
else
    echo "5️⃣  Skipping tests (pytest not installed)"
fi

# 6. Type Checking (if mypy available)
if command -v mypy >/dev/null 2>&1; then
    echo "6️⃣  Running mypy type checker..."
    mypy core/ --ignore-missing-imports --no-strict-optional > "$REPORT_DIR/mypy_${TIMESTAMP}.txt" 2>&1 || true
    MYPY_ERRORS=$(grep -c "error:" "$REPORT_DIR/mypy_${TIMESTAMP}.txt" 2>/dev/null || echo "0")
    echo -e "   ${YELLOW}Type errors: $MYPY_ERRORS${NC}"
else
    echo "6️⃣  Skipping type checking (mypy not installed)"
fi

# Generate Summary Report
echo ""
echo "📝 Generating summary report..."
SUMMARY_FILE="$REPORT_DIR/SUMMARY_${TIMESTAMP}.txt"

cat > "$SUMMARY_FILE" <<EOF
====================================
Code Quality Report Summary
====================================
Generated: $(date)
Report ID: ${TIMESTAMP}

STATIC ANALYSIS RESULTS
-----------------------
Ruff Issues: $RUFF_COUNT
Flake8 Critical: $FLAKE8_CRITICAL
Black Formatting: $BLACK_FILES files need formatting

SECURITY ANALYSIS
-----------------
Bandit High Severity: ${BANDIT_HIGH:-N/A}
Bandit Medium Severity: ${BANDIT_MEDIUM:-N/A}

TEST RESULTS
------------
Tests Passed: ${TEST_PASSED:-N/A}
Tests Failed: ${TEST_FAILED:-N/A}

TYPE CHECKING
-------------
MyPy Errors: ${MYPY_ERRORS:-N/A}

DETAILED REPORTS
----------------
All detailed reports saved to: $REPORT_DIR/

Files generated:
- ruff_${TIMESTAMP}.txt
- ruff_stats_${TIMESTAMP}.txt
- flake8_critical_${TIMESTAMP}.txt
- flake8_full_${TIMESTAMP}.txt
- bandit_${TIMESTAMP}.json
- bandit_${TIMESTAMP}.txt
- black_${TIMESTAMP}.txt
EOF

if [ -f "$REPORT_DIR/pytest_${TIMESTAMP}.txt" ]; then
    echo "- pytest_${TIMESTAMP}.txt" >> "$SUMMARY_FILE"
fi

if [ -f "$REPORT_DIR/mypy_${TIMESTAMP}.txt" ]; then
    echo "- mypy_${TIMESTAMP}.txt" >> "$SUMMARY_FILE"
fi

cat >> "$SUMMARY_FILE" <<EOF

NEXT STEPS
----------
1. Review detailed reports in $REPORT_DIR/
2. Prioritize issues based on severity
3. Update CODE_QUALITY_REPORT.md with findings
4. Create GitHub issues for tracking
5. Begin refactoring following REFACTORING_TASKS.md

====================================
EOF

# Display summary
echo ""
cat "$SUMMARY_FILE"
echo ""
echo -e "${GREEN}✅ Quality report generation complete!${NC}"
echo ""
echo "📁 Reports saved to: $REPORT_DIR/"
echo "📄 Summary: $SUMMARY_FILE"
echo ""
echo "To view detailed reports:"
echo "  cat $REPORT_DIR/ruff_stats_${TIMESTAMP}.txt"
echo "  cat $REPORT_DIR/bandit_${TIMESTAMP}.txt"
echo "  cat $REPORT_DIR/SUMMARY_${TIMESTAMP}.txt"
echo ""
