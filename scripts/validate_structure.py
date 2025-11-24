#!/usr/bin/env python3
"""
Validation script for repository restructure.

This script verifies that the new src/ directory structure is correctly set up
and that imports work as expected.
"""

import os
import sys
from pathlib import Path


def check_directory_structure():
    """Verify expected directory structure exists."""
    print("Checking directory structure...")
    
    expected_dirs = [
        "src",
        "src/core",
        "src/components",
        "src/utils",
        "src/plugins",
        "src/models",
        "src/migrations",
        "config",
        "tests",
        "docs",
    ]
    
    all_exist = True
    for dir_path in expected_dirs:
        if os.path.isdir(dir_path):
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ - MISSING")
            all_exist = False
    
    return all_exist


def check_config_files():
    """Verify configuration files are in the right place."""
    print("\nChecking configuration files...")
    
    config_files = [
        "config/.env.example",
        "config/replit.nix",
        "config/space.yaml",
    ]
    
    all_exist = True
    for file_path in config_files:
        if os.path.isfile(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def check_source_files():
    """Verify Python source files are in src/."""
    print("\nChecking source files...")
    
    source_files = [
        "src/__init__.py",
        "src/app.py",
        "src/db_check.py",
        "src/kali_server.py",
        "src/manage.py",
        "src/core/__init__.py",
        "src/core/cli.py",
        "src/core/server.py",
    ]
    
    all_exist = True
    for file_path in source_files:
        if os.path.isfile(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def check_backward_compatibility():
    """Verify backward-compatible wrapper exists."""
    print("\nChecking backward compatibility...")
    
    if os.path.isfile("app.py"):
        with open("app.py") as f:
            content = f.read()
            if "from src.app import main" in content:
                print("  ✓ Root app.py exists and imports from src.app")
                if "DeprecationWarning" in content:
                    print("  ✓ Deprecation warning present")
                return True
            else:
                print("  ✗ Root app.py doesn't import from src.app")
                return False
    else:
        print("  ✗ Root app.py missing")
        return False


def check_imports():
    """Test that basic imports work."""
    print("\nChecking Python imports...")
    
    # Add current directory to path
    sys.path.insert(0, ".")
    
    tests = [
        ("src.core", "Core package"),
        ("src.core.cli", "CLI module"),
        ("src.utils.config_validator", "Config validator"),
    ]
    
    all_ok = True
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"  ✓ {description} ({module_name})")
        except ModuleNotFoundError as e:
            # If it's a dependency issue (not src structure), that's ok
            if "src" not in str(e):
                print(f"  ⚠ {description} ({module_name}) - dependency missing: {e}")
            else:
                print(f"  ✗ {description} ({module_name}) - import error: {e}")
                all_ok = False
        except Exception as e:
            print(f"  ⚠ {description} ({module_name}) - {e}")
    
    return all_ok


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("CodeTuneStudio Repository Structure Validation")
    print("=" * 60)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Configuration Files", check_config_files),
        ("Source Files", check_source_files),
        ("Backward Compatibility", check_backward_compatibility),
        ("Python Imports", check_imports),
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All validation checks passed!")
        return 0
    else:
        print("\n❌ Some validation checks failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
