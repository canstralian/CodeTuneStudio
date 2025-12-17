"""
Rules Engine - Defines review rules for safety, clarity, and maintainability.

Each rule is explicit, deterministic where possible, and provides clear explanations.
"""

import re
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .types import Rule, Violation, Category, Severity

logger = logging.getLogger(__name__)


# ============================================================================
# SAFETY RULES (Critical - Always Fail Build)
# ============================================================================

SECURITY_RULES = [
    Rule(
        id="SEC001",
        category=Category.SAFETY,
        severity=Severity.CRITICAL,
        name="SQL Injection via String Concatenation",
        description="SQL query using string concatenation or f-strings detected",
        pattern=r'(execute|query)\s*\(\s*["\'].*(%s|%d|\+|f["\'])',
        documentation_url="https://owasp.org/www-community/attacks/SQL_Injection",
        llm_prompt="Check for SQL injection vulnerabilities from string concatenation or formatting in database queries",
    ),
    Rule(
        id="SEC002",
        category=Category.SAFETY,
        severity=Severity.CRITICAL,
        name="Hardcoded Credentials",
        description="Hardcoded password, API key, secret, or token detected",
        pattern=r'(password|api_key|secret|token|apikey|auth_token)\s*=\s*["\'][^"\']{8,}["\']',
        documentation_url="https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure",
        llm_prompt="Check for hardcoded credentials, API keys, passwords, or secrets",
    ),
    Rule(
        id="SEC003",
        category=Category.SAFETY,
        severity=Severity.CRITICAL,
        name="Command Injection Risk",
        description="System command execution with user input detected",
        pattern=r'(os\.system|subprocess\.(call|run|Popen))\s*\([^)]*(%s|f["\']|\+)',
        documentation_url="https://owasp.org/www-community/attacks/Command_Injection",
        llm_prompt="Check for command injection vulnerabilities in system calls",
    ),
    Rule(
        id="SEC004",
        category=Category.SAFETY,
        severity=Severity.CRITICAL,
        name="Insecure Deserialization",
        description="Unsafe deserialization of untrusted data",
        pattern=r'(pickle\.loads?|yaml\.load\(|eval\()',
        documentation_url="https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data",
        llm_prompt="Check for insecure deserialization of untrusted data",
    ),
    Rule(
        id="SEC005",
        category=Category.SAFETY,
        severity=Severity.CRITICAL,
        name="Path Traversal Vulnerability",
        description="File path operations without validation detected",
        pattern=r'open\s*\([^)]*\+.*\)|os\.path\.join\s*\([^)]*\+',
        documentation_url="https://owasp.org/www-community/attacks/Path_Traversal",
        llm_prompt="Check for path traversal vulnerabilities in file operations",
    ),
    Rule(
        id="SEC006",
        category=Category.SAFETY,
        severity=Severity.CRITICAL,
        name="XSS via Unsafe HTML Rendering",
        description="Unsafe HTML rendering without escaping",
        pattern=r'(innerHTML|dangerouslySetInnerHTML|unsafe_allow_html\s*=\s*True)',
        documentation_url="https://owasp.org/www-community/attacks/xss/",
        llm_prompt="Check for cross-site scripting (XSS) vulnerabilities",
    ),
    Rule(
        id="SEC007",
        category=Category.SAFETY,
        severity=Severity.CRITICAL,
        name="Debug Mode in Production",
        description="Debug mode enabled or debug information exposed",
        pattern=r'(DEBUG\s*=\s*True|app\.debug\s*=\s*True|\.env\s+debug)',
        documentation_url="https://owasp.org/www-project-top-ten/",
        llm_prompt="Check if debug mode is enabled in production configuration",
    ),
]

# ============================================================================
# CLARITY RULES (Warning - Fail in Strict Mode)
# ============================================================================

CLARITY_RULES = [
    Rule(
        id="CLR001",
        category=Category.CLARITY,
        severity=Severity.WARNING,
        name="Missing Function Docstring",
        description="Public function missing docstring",
        pattern=r'^def\s+[a-z_][a-z0-9_]*\s*\([^)]*\)\s*:\s*\n(?!\s*["\'\(])',
        llm_prompt="Check if public functions have comprehensive docstrings",
    ),
    Rule(
        id="CLR002",
        category=Category.CLARITY,
        severity=Severity.WARNING,
        name="Single Letter Variable Name",
        description="Single-letter variable name in non-trivial scope",
        pattern=r'\b([a-z])\s*=\s*(?!range|enumerate)',
        llm_prompt="Check for unclear single-letter variable names outside loops",
    ),
    Rule(
        id="CLR003",
        category=Category.CLARITY,
        severity=Severity.WARNING,
        name="Magic Number Without Explanation",
        description="Magic number used without constant or comment",
        pattern=r'[^a-zA-Z0-9_](\d{2,})[^a-zA-Z0-9_]',
        llm_prompt="Check for magic numbers without explanation or named constants",
    ),
    Rule(
        id="CLR004",
        category=Category.CLARITY,
        severity=Severity.WARNING,
        name="Complex Boolean Expression",
        description="Complex boolean expression without clarifying variables",
        pattern=r'(and|or).*\1.*\1',  # Multiple and/or in single expression
        llm_prompt="Check for complex boolean expressions that should be simplified",
    ),
    Rule(
        id="CLR005",
        category=Category.CLARITY,
        severity=Severity.WARNING,
        name="Missing Type Hints",
        description="Function missing type hints for parameters or return",
        pattern=r'^def\s+[a-z_][a-z0-9_]*\s*\(([^):]*)\)\s*:',
        llm_prompt="Check if functions have type hints for all parameters and return values",
    ),
]

# ============================================================================
# MAINTAINABILITY RULES (Warning - Fail in Strict Mode)
# ============================================================================

MAINTAINABILITY_RULES = [
    Rule(
        id="MNT001",
        category=Category.MAINTAINABILITY,
        severity=Severity.WARNING,
        name="Duplicate Code Block",
        description="Duplicate code block detected",
        llm_prompt="Check for duplicate code that should be extracted into a function",
    ),
    Rule(
        id="MNT002",
        category=Category.MAINTAINABILITY,
        severity=Severity.WARNING,
        name="Function Too Long",
        description="Function exceeds recommended length (>50 lines)",
        llm_prompt="Check if function is too long and should be split into smaller functions",
    ),
    Rule(
        id="MNT003",
        category=Category.MAINTAINABILITY,
        severity=Severity.WARNING,
        name="High Cyclomatic Complexity",
        description="Function has high cyclomatic complexity (>10)",
        llm_prompt="Check for high cyclomatic complexity that makes code hard to test and maintain",
    ),
    Rule(
        id="MNT004",
        category=Category.MAINTAINABILITY,
        severity=Severity.WARNING,
        name="Missing Error Handling",
        description="Function performs risky operations without error handling",
        pattern=r'(open\(|requests\.(get|post)|json\.loads)\s*\([^)]*\)(?!\s*(except|\.get\())',
        llm_prompt="Check for missing error handling on operations that can fail",
    ),
    Rule(
        id="MNT005",
        category=Category.MAINTAINABILITY,
        severity=Severity.WARNING,
        name="God Object/Class",
        description="Class has too many methods or responsibilities",
        llm_prompt="Check if class has too many responsibilities and violates SRP",
    ),
    Rule(
        id="MNT006",
        category=Category.MAINTAINABILITY,
        severity=Severity.WARNING,
        name="Tight Coupling",
        description="Code is tightly coupled to implementation details",
        llm_prompt="Check for tight coupling that makes code hard to test or modify",
    ),
    Rule(
        id="MNT007",
        category=Category.MAINTAINABILITY,
        severity=Severity.WARNING,
        name="Inconsistent Naming Convention",
        description="Inconsistent naming convention used",
        llm_prompt="Check for inconsistent naming conventions (camelCase vs snake_case)",
    ),
]


class RulesEngine:
    """
    Applies review rules to code changes.

    Supports both pattern-based (regex) and LLM-based rule checking.
    """

    def __init__(self, custom_rules: Optional[List[Rule]] = None):
        """
        Initialize rules engine.

        Args:
            custom_rules: Optional list of project-specific custom rules
        """
        self.rules: List[Rule] = []
        self.rules.extend(SECURITY_RULES)
        self.rules.extend(CLARITY_RULES)
        self.rules.extend(MAINTAINABILITY_RULES)

        if custom_rules:
            self.rules.extend(custom_rules)

        logger.info(f"Loaded {len(self.rules)} review rules")

    def get_rules_by_category(self, category: Category) -> List[Rule]:
        """Get all rules for a specific category."""
        return [rule for rule in self.rules if rule.category == category]

    def get_rules_by_severity(self, severity: Severity) -> List[Rule]:
        """Get all rules with specific severity."""
        return [rule for rule in self.rules if rule.severity == severity]

    def get_critical_rules(self) -> List[Rule]:
        """Get all critical rules."""
        return self.get_rules_by_severity(Severity.CRITICAL)

    def check_pattern_rule(
        self, rule: Rule, code: str, filepath: str
    ) -> List[Violation]:
        """
        Check a pattern-based rule against code.

        Args:
            rule: Rule to check
            code: Code content to analyze
            filepath: Path to file being analyzed

        Returns:
            List of violations found
        """
        if not rule.pattern:
            return []

        violations = []

        try:
            pattern = re.compile(rule.pattern, re.MULTILINE)
            lines = code.split("\n")

            for line_num, line in enumerate(lines, start=1):
                matches = pattern.finditer(line)
                for match in matches:
                    violation = Violation(
                        rule_id=rule.id,
                        file_path=filepath,
                        line_start=line_num,
                        line_end=line_num,
                        column_start=match.start(),
                        column_end=match.end(),
                        message=rule.description,
                        code_snippet=line.strip(),
                    )
                    violations.append(violation)

        except re.error as e:
            logger.error(f"Invalid regex pattern for rule {rule.id}: {e}")

        return violations

    def check_all_rules(
        self, code: str, filepath: str, language: str = "python"
    ) -> List[Violation]:
        """
        Check all applicable rules against code.

        Args:
            code: Code content to analyze
            filepath: Path to file being analyzed
            language: Programming language of the code

        Returns:
            List of all violations found
        """
        violations = []

        # Apply pattern-based rules
        for rule in self.rules:
            if not rule.enabled:
                continue

            if rule.pattern:
                rule_violations = self.check_pattern_rule(rule, code, filepath)
                violations.extend(rule_violations)

        logger.info(f"Found {len(violations)} pattern-based violations in {filepath}")
        return violations

    def explain_violation(self, violation: Violation) -> Dict[str, str]:
        """
        Generate detailed explanation for a violation.

        Args:
            violation: Violation to explain

        Returns:
            Dictionary with explanation details
        """
        rule = next((r for r in self.rules if r.id == violation.rule_id), None)
        if not rule:
            return {
                "title": "Unknown Rule",
                "description": "Rule not found",
                "explanation": "",
            }

        explanation = {
            "title": rule.name,
            "description": rule.description,
            "category": rule.category.value,
            "severity": rule.severity.value,
        }

        # Add category-specific explanation
        if rule.category == Category.SAFETY:
            explanation["why_matters"] = (
                "This is a security vulnerability that could be exploited "
                "by attackers to compromise the system, access sensitive data, "
                "or execute unauthorized operations."
            )
        elif rule.category == Category.CLARITY:
            explanation["why_matters"] = (
                "This affects code readability and makes it harder for other "
                "developers (including your future self) to understand and "
                "maintain the code."
            )
        else:  # MAINTAINABILITY
            explanation["why_matters"] = (
                "This creates technical debt that will make future changes "
                "more difficult, time-consuming, and error-prone."
            )

        if rule.documentation_url:
            explanation["learn_more"] = rule.documentation_url

        return explanation
