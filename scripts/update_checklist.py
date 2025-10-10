"""
Script to automatically update the PR review checklist.

This script fetches closed PRs from the GitHub API and updates the
PR_REVIEW_CHECKLIST.md file to mark merged PRs as completed.

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token (required)

Usage:
    python scripts/update_checklist.py
"""

import os
import sys
from typing import Dict, List, Any

import requests
from dotenv import load_dotenv


def load_environment() -> None:
    """
    Load environment variables from .env file.

    Uses python-dotenv to securely load environment variables from a .env file
    if it exists. This allows for secure credential management without
    hardcoding sensitive information.
    """
    load_dotenv()


def validate_github_token() -> str:
    """
    Validate and retrieve the GitHub token from environment variables.

    Returns:
        str: The GitHub token

    Raises:
        SystemExit: If GITHUB_TOKEN is not set or is empty, exits with code 1

    Example:
        >>> os.environ['GITHUB_TOKEN'] = 'ghp_test123'
        >>> token = validate_github_token()
        >>> assert token == 'ghp_test123'
    """
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print(
            "Error: GITHUB_TOKEN environment variable is not set.",
            file=sys.stderr
        )
        print(
            "Please set GITHUB_TOKEN in your environment or .env file.",
            file=sys.stderr
        )
        print(
            "For more information, see .env.example",
            file=sys.stderr
        )
        sys.exit(1)

    if not token.strip():
        print(
            "Error: GITHUB_TOKEN is empty.",
            file=sys.stderr
        )
        sys.exit(1)

    return token


def fetch_closed_prs(
    repo: str,
    token: str
) -> List[Dict[str, Any]]:
    """
    Fetch closed pull requests from the GitHub API.

    Args:
        repo: Repository identifier in format 'owner/repo'
        token: GitHub personal access token for authentication

    Returns:
        List of PR dictionaries from GitHub API

    Raises:
        requests.exceptions.RequestException: If API request fails
        SystemExit: If API returns non-200 status code

    Example:
        >>> prs = fetch_closed_prs('owner/repo', 'token123')
        >>> isinstance(prs, list)
        True
    """
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo}/pulls?state=closed"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch PRs from GitHub API: {e}", file=sys.stderr)
        sys.exit(1)

    return response.json()


def read_checklist_file(filepath: str) -> List[str]:
    """
    Read the checklist file and return its lines.

    Args:
        filepath: Path to the checklist file

    Returns:
        List of lines from the checklist file

    Raises:
        SystemExit: If file cannot be read
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines
    except FileNotFoundError:
        print(
            f"Error: Checklist file '{filepath}' not found.",
            file=sys.stderr
        )
        sys.exit(1)
    except OSError as e:
        print(
            f"Error reading checklist file '{filepath}': {e}",
            file=sys.stderr
        )
        sys.exit(1)


def update_checklist_lines(
    lines: List[str],
    prs: List[Dict[str, Any]]
) -> List[str]:
    """
    Update checklist lines to mark merged PRs as completed.

    Args:
        lines: List of lines from the checklist file
        prs: List of PR dictionaries from GitHub API

    Returns:
        Updated list of lines with merged PRs marked as completed

    Example:
        >>> lines = ['- [ ] PR #123 Something', '- [ ] PR #456 Other']
        >>> prs = [{'number': 123, 'merged_at': '2024-01-01'}]
        >>> updated = update_checklist_lines(lines, prs)
        >>> '- [x] PR #123 Something' in updated[0]
        True
    """
    updated_lines = lines.copy()

    for i, line in enumerate(updated_lines):
        for pr in prs:
            pr_marker = f"PR #{pr['number']}"
            if pr_marker in line and pr.get("merged_at"):
                # Replace unchecked box with checked box
                updated_lines[i] = line.replace("[ ]", "[x]")
                break  # Move to next line after updating

    return updated_lines


def write_checklist_file(filepath: str, lines: List[str]) -> None:
    """
    Write updated lines back to the checklist file.

    Args:
        filepath: Path to the checklist file
        lines: Updated list of lines to write

    Raises:
        SystemExit: If file cannot be written
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Successfully updated checklist: {filepath}")
    except (IOError, OSError) as e:
        print(
            f"Error writing to {filepath}: {e}",
            file=sys.stderr
        )
        sys.exit(1)


def main() -> None:
    """
    Main function to update the PR review checklist.

    This function orchestrates the entire process:
    1. Loads environment variables
    2. Validates GitHub token
    3. Fetches closed PRs
    4. Reads checklist file
    5. Updates checklist with merged PRs
    6. Writes updated checklist back to file
    """
    # Configuration
    REPO = "canstralian/CodeTuneStudio"
    CHECKLIST_PATH = "PR_REVIEW_CHECKLIST.md"

    # Load environment variables from .env file
    load_environment()

    # Validate GitHub token
    github_token = validate_github_token()

    # Fetch closed PRs from GitHub
    print(f"Fetching closed PRs from {REPO}...")
    prs = fetch_closed_prs(REPO, github_token)
    print(f"Found {len(prs)} closed PRs")

    # Read checklist file
    print(f"Reading checklist from {CHECKLIST_PATH}...")
    lines = read_checklist_file(CHECKLIST_PATH)

    # Update checklist for merged PRs
    print("Updating checklist...")
    updated_lines = update_checklist_lines(lines, prs)

    # Write updated checklist
    write_checklist_file(CHECKLIST_PATH, updated_lines)
    print("Checklist update complete!")


if __name__ == "__main__":
    main()
