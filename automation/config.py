"""
Configuration for GitHub Automation Tools

This module provides centralized configuration for all automation scripts.
"""

import os
from typing import Dict, Any


# Repository Configuration
REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "canstralian")
REPO_NAME = os.getenv("GITHUB_REPO_NAME", "CodeTuneStudio")

# Default branch settings
DEFAULT_BASE_BRANCH = "main"
ALLOWED_BASE_BRANCHES = ["main", "develop", "staging"]

# GitHub API Configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"

# Default labels for different issue types
DEFAULT_LABELS: Dict[str, list] = {
    "bug": ["bug"],
    "feature": ["enhancement"],
    "documentation": ["documentation"],
    "enhancement": ["enhancement"],
    "task": ["task"]
}

# Rate limiting settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RATE_LIMIT_BUFFER = 100  # Keep this many requests in reserve

# Automation behavior
AUTO_ASSIGN_ISSUES = os.getenv("AUTO_ASSIGN_ISSUES", "false").lower() == "true"
DEFAULT_ASSIGNEE = os.getenv("DEFAULT_ISSUE_ASSIGNEE", None)

# Logging
VERBOSE = os.getenv("AUTOMATION_VERBOSE", "false").lower() == "true"

# Project management
DEFAULT_PROJECT_COLUMNS = ["To Do", "In Progress", "Review", "Done"]


def get_config() -> Dict[str, Any]:
    """
    Get complete configuration dictionary.
    
    Returns:
        Dictionary containing all configuration values
    """
    return {
        "repo_owner": REPO_OWNER,
        "repo_name": REPO_NAME,
        "default_base_branch": DEFAULT_BASE_BRANCH,
        "allowed_base_branches": ALLOWED_BASE_BRANCHES,
        "github_api_url": GITHUB_API_URL,
        "github_api_version": GITHUB_API_VERSION,
        "default_labels": DEFAULT_LABELS,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
        "rate_limit_buffer": RATE_LIMIT_BUFFER,
        "auto_assign_issues": AUTO_ASSIGN_ISSUES,
        "default_assignee": DEFAULT_ASSIGNEE,
        "verbose": VERBOSE,
        "default_project_columns": DEFAULT_PROJECT_COLUMNS,
    }


def validate_config() -> bool:
    """
    Validate configuration settings.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    errors = []
    
    if not REPO_OWNER:
        errors.append("REPO_OWNER is not set")
    
    if not REPO_NAME:
        errors.append("REPO_NAME is not set")
    
    if DEFAULT_BASE_BRANCH not in ALLOWED_BASE_BRANCHES:
        errors.append(
            f"DEFAULT_BASE_BRANCH '{DEFAULT_BASE_BRANCH}' not in "
            f"ALLOWED_BASE_BRANCHES: {ALLOWED_BASE_BRANCHES}"
        )
    
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True
