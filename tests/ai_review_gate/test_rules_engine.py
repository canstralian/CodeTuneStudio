"""Tests for Rules Engine component."""

import pytest
from scripts.ai_review_gate.rules import RulesEngine, SECURITY_RULES
from scripts.ai_review_gate.types import Category, Severity


@pytest.fixture
def rules_engine():
    """Create a RulesEngine instance."""
    return RulesEngine()


def test_rules_loaded(rules_engine):
    """Test that rules are properly loaded."""
    assert len(rules_engine.rules) > 0
    assert len(rules_engine.get_critical_rules()) > 0


def test_sql_injection_detection(rules_engine):
    """Test SQL injection pattern detection."""
    # Vulnerable code
    vulnerable_code = 'query = f"SELECT * FROM users WHERE id = {user_id}"'

    violations = rules_engine.check_all_rules(vulnerable_code, "app.py")

    # Should detect SQL injection
    sql_violations = [v for v in violations if v.rule_id == "SEC001"]
    assert len(sql_violations) > 0


def test_hardcoded_credentials_detection(rules_engine):
    """Test hardcoded credentials detection."""
    vulnerable_code = 'api_key = "sk-1234567890abcdef"'

    violations = rules_engine.check_all_rules(vulnerable_code, "config.py")

    # Should detect hardcoded credentials
    cred_violations = [v for v in violations if v.rule_id == "SEC002"]
    assert len(cred_violations) > 0


def test_command_injection_detection(rules_engine):
    """Test command injection detection."""
    vulnerable_code = 'os.system(f"ls {user_input}")'

    violations = rules_engine.check_all_rules(vulnerable_code, "utils.py")

    # Should detect command injection
    cmd_violations = [v for v in violations if v.rule_id == "SEC003"]
    assert len(cmd_violations) > 0


def test_safe_code_no_violations(rules_engine):
    """Test that safe code doesn't trigger false positives."""
    safe_code = """
def get_user(user_id: int) -> Optional[User]:
    '''Retrieve user by ID using parameterized query.'''
    query = "SELECT * FROM users WHERE id = ?"
    result = db.execute(query, (user_id,))
    return result.fetchone()
"""

    violations = rules_engine.check_all_rules(safe_code, "database.py")

    # Should not detect SQL injection in safe code
    sql_violations = [v for v in violations if v.rule_id == "SEC001"]
    assert len(sql_violations) == 0


def test_get_rules_by_category(rules_engine):
    """Test filtering rules by category."""
    safety_rules = rules_engine.get_rules_by_category(Category.SAFETY)
    clarity_rules = rules_engine.get_rules_by_category(Category.CLARITY)

    assert len(safety_rules) > 0
    assert len(clarity_rules) > 0
    assert all(r.category == Category.SAFETY for r in safety_rules)


def test_get_rules_by_severity(rules_engine):
    """Test filtering rules by severity."""
    critical_rules = rules_engine.get_rules_by_severity(Severity.CRITICAL)
    warning_rules = rules_engine.get_rules_by_severity(Severity.WARNING)

    assert len(critical_rules) > 0
    assert len(warning_rules) > 0
    assert all(r.severity == Severity.CRITICAL for r in critical_rules)


def test_violation_explanation(rules_engine):
    """Test that violations can be explained."""
    vulnerable_code = 'password = "hardcoded123"'

    violations = rules_engine.check_all_rules(vulnerable_code, "config.py")
    assert len(violations) > 0

    explanation = rules_engine.explain_violation(violations[0])

    assert "title" in explanation
    assert "description" in explanation
    assert "why_matters" in explanation
    assert len(explanation["why_matters"]) > 0


def test_pattern_based_detection(rules_engine):
    """Test that pattern-based rules work correctly."""
    # Test missing error handling
    code_without_error_handling = """
file_data = open('data.txt').read()
json_data = json.loads(file_data)
"""

    violations = rules_engine.check_all_rules(code_without_error_handling, "parser.py")

    # Should detect missing error handling
    error_handling_violations = [v for v in violations if v.rule_id == "MNT004"]
    assert len(error_handling_violations) > 0
