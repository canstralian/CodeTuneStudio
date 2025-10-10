#!/usr/bin/env python3
"""
Security checker script for CodeTuneStudio.

This script checks for common security issues in the codebase.
Run this before committing code to catch security problems early.

Usage:
    python scripts/security_check.py [directory]

Example:
    python scripts/security_check.py utils/
    python scripts/security_check.py .
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


class SecurityChecker:
    """Check code for common security issues."""

    def _redact_secret_line(self, line: str) -> str:
        """
        Redact the value of suspected secrets in a line.
        Replaces values assigned to secret key variables with ***REDACTED***.
        """
        # Example pattern: SECRET_KEY = "value" or SECRET_KEY = 'value'
        # Replace value after = with ***REDACTED*** for common secret assignment forms
        # Will catch lines like: SOME_KEY = "12345", password = 'abcdef'
        # Replace quoted assignments
        line = re.sub(r'([\'"])[^'"]+\1', r'\1***REDACTED***\1', line)
        # Replace bare variable = value
        line = re.sub(r'(=\s*)([A-Za-z0-9@#\-_]{4,})', r'\1***REDACTED***', line)
        # Replace : value in dicts/yaml: key: value
        line = re.sub(r'(:\s*)([A-Za-z0-9@#\-_]{4,})', r'\1***REDACTED***', line)
        return line
    
    def __init__(self, directory: str = "."):
        """
        Initialize security checker.
        
        Args:
            directory: Directory to scan
        """
        self.directory = directory
        self.issues = []
        
    def check_exec_calls(self) -> List[Tuple[str, int, str]]:
        """
        Find direct exec() calls.
        
        Returns:
            List of (filename, line_number, line_content) tuples
        """
        print("🔍 Checking for direct exec() calls...")
        issues = []
        
        for py_file in Path(self.directory).rglob("*.py"):
            # Skip excluded paths
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
            # Skip security.py itself (it has documented examples)
            if py_file.name == "security.py":
                continue
                
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Skip comments
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        continue
                    
                    # Look for actual exec() calls
                    if re.search(r'\bexec\s*\(', line):
                        issues.append((str(py_file), line_num, line.strip()))
        
        return issues
    
    def check_sql_concatenation(self) -> List[Tuple[str, int, str]]:
        """
        Find potential SQL injection via string concatenation.
        
        Returns:
            List of (filename, line_number, line_content) tuples
        """
        print("🔍 Checking for SQL string concatenation...")
        issues = []
        
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE']
        
        for py_file in Path(self.directory).rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Check for f-strings or format with SQL keywords
                    for keyword in sql_keywords:
                        if keyword in line.upper():
                            if re.search(r'f["\'].*{.*}|\.format\(|%\s*\(', line):
                                issues.append((str(py_file), line_num, line.strip()))
                                break
        
        return issues
    
    def check_hardcoded_secrets(self) -> List[Tuple[str, int, str]]:
        """
        Find potential hardcoded secrets.
        
        Returns:
            List of (filename, line_number, line_content) tuples
        """
        print("🔍 Checking for hardcoded secrets...")
        issues = []
        
        secret_patterns = [
            r'(api_key|apikey)\s*=\s*["\'][^"\']+["\']',
            r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            r'(secret|token)\s*=\s*["\'][^"\']+["\']',
            r'(aws_access_key|aws_secret)',
        ]
        
        for py_file in Path(self.directory).rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Skip comments and environment variable usage
                    if line.strip().startswith('#') or 'os.environ' in line or 'os.getenv' in line:
                        continue
                    
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append((str(py_file), line_num, line.strip()))
                            break
        
        return issues
    
    def check_input_validation(self) -> List[Tuple[str, int, str]]:
        """
        Find potential missing input validation in API endpoints.
        
        Returns:
            List of (filename, line_number, line_content) tuples
        """
        print("🔍 Checking for potential missing input validation...")
        issues = []
        
        for py_file in Path(self.directory).rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Look for Flask routes without validation decorators
                for line_num, line in enumerate(lines, 1):
                    if '@app.route' in line or '@blueprint.route' in line:
                        # Check next few lines for validation
                        next_lines = '\n'.join(lines[line_num:line_num+5])
                        if 'request.get_json()' in next_lines or 'request.form' in next_lines:
                            if '@validate_json_input' not in next_lines and 'sanitize' not in next_lines:
                                issues.append((
                                    str(py_file),
                                    line_num,
                                    f"Route may need input validation: {line.strip()}"
                                ))
        
        return issues
    
    def run_bandit(self) -> bool:
        """
        Run bandit security scanner if available.
        
        Returns:
            True if bandit passed, False otherwise
        """
        print("🔍 Running Bandit security scanner...")
        
        try:
            result = subprocess.run(
                ['bandit', '-r', self.directory, '-f', 'screen'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Bandit scan passed")
                return True
            else:
                print("⚠️  Bandit found issues:")
                print(result.stdout)
                return False
                
        except FileNotFoundError:
            print("ℹ️  Bandit not installed. Install with: pip install bandit")
            return True
        except subprocess.TimeoutExpired:
            print("⚠️  Bandit scan timed out")
            return False
    
    def run_safety(self) -> bool:
        """
        Run safety dependency scanner if available.
        
        Returns:
            True if safety passed, False otherwise
        """
        print("🔍 Running Safety dependency scanner...")
        
        try:
            result = subprocess.run(
                ['safety', 'check', '--output', 'screen'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Safety scan passed")
                return True
            else:
                print("⚠️  Safety found vulnerabilities:")
                print(result.stdout)
                return False
                
        except FileNotFoundError:
            print("ℹ️  Safety not installed. Install with: pip install safety")
            return True
        except subprocess.TimeoutExpired:
            print("⚠️  Safety scan timed out")
            return False
    
    def print_issues(self, title: str, issues: List[Tuple[str, int, str]]):
        """Print formatted issues."""
        if not issues:
            print(f"✅ No issues found for: {title}")
            return
        
        print(f"\n⚠️  {title} ({len(issues)} issues):")
        for filename, line_num, line in issues:
            print(f"  {filename}:{line_num}")
            # Redact suspected secrets if title indicates secret findings
            if title.lower().startswith("potential hardcoded secrets"):
                print(f"    {self._redact_secret_line(line)[:100]}")
            else:
                print(f"    {line[:100]}")
    def run_all_checks(self) -> bool:
        """
        Run all security checks.
        
        Returns:
            True if all checks passed, False otherwise
        """
        print("=" * 60)
        print("🔒 CodeTuneStudio Security Checker")
        print("=" * 60)
        print(f"Scanning directory: {self.directory}\n")
        
        all_passed = True
        
        # Check for exec() calls
        exec_issues = self.check_exec_calls()
        self.print_issues("Direct exec() calls found", exec_issues)
        if exec_issues:
            all_passed = False
        
        # Check for SQL concatenation
        sql_issues = self.check_sql_concatenation()
        self.print_issues("Potential SQL injection via concatenation", sql_issues)
        if sql_issues:
            all_passed = False
        
        # Check for hardcoded secrets
        secret_issues = self.check_hardcoded_secrets()
        self.print_issues("Potential hardcoded secrets", secret_issues)
        if secret_issues:
            all_passed = False
        
        # Check for missing input validation
        validation_issues = self.check_input_validation()
        self.print_issues("Routes that may need input validation", validation_issues)
        if validation_issues:
            print("ℹ️  Note: These are suggestions, review manually")
        
        print("\n" + "=" * 60)
        
        # Run external scanners
        bandit_passed = self.run_bandit()
        safety_passed = self.run_safety()
        
        print("\n" + "=" * 60)
        
        if all_passed and bandit_passed and safety_passed:
            print("✅ All security checks passed!")
            return True
        else:
            print("⚠️  Some security checks failed. Please review the issues above.")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check CodeTuneStudio code for security issues"
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' not found")
        sys.exit(1)
    
    checker = SecurityChecker(args.directory)
    passed = checker.run_all_checks()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
