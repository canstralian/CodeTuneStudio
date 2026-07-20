#!/usr/bin/env python3
"""
GitHub PR Cleanup Script
Automates closing of stale and redundant pull requests.
"""

import os
import sys

import requests

# Configuration
REPO_OWNER = "canstralian"
REPO_NAME = "CodeTuneStudio"
GITHUB_API = "https://api.github.com"

# Categories of PRs to close
STALE_PRS = {
    "security_autofix": [28, 35, 53],
    "september_prs": [5, 21, 25, 26],
    "october_prs": [
        28,
        33,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        45,
        46,
        50,
        53,
        55,
        59,
        64,
        67,
        68,
    ],
    "duplicate_docs": [99, 103, 105, 118, 119, 121, 149, 151, 152, 153],
    "duplicate_ci": [96, 97, 111, 144],
    "duplicate_formatting": [33, 55, 59, 108, 156],
    "duplicate_dependencies": [82, 109, 110, 111, 112, 124],
    "duplicate_refactoring": [93, 94, 116],
    "merge_conflicts": [92, 106, 107],
    "duplicate_logging": [113],
    "wip_and_reports": [21, 131, 125, 143],
}

CLOSURE_MESSAGES = {
    "security_autofix": (
        "Closing this automated security fix as it is stale (2+ months old). "
        "Security issues should be addressed with fresh fixes that account for "
        "the current codebase state. See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "september_prs": (
        "Closing this PR as it is stale (3+ months old with no recent activity). "
        "If this change is still needed, please create a fresh PR with updated "
        "changes that account for the current codebase state. "
        "See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "october_prs": (
        "Closing this PR as it is stale (2+ months old with no recent activity). "
        "If this change is still needed, please create a fresh PR with updated "
        "changes. See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "duplicate_docs": (
        "Closing as redundant. Multiple PRs are attempting to consolidate "
        "documentation. We are keeping the most comprehensive recent PR. "
        "See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "duplicate_ci": (
        "Closing as redundant. Multiple PRs are attempting to fix CI issues. "
        "We are keeping the most recent comprehensive fix. "
        "See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "duplicate_formatting": (
        "Closing as redundant. Multiple PRs are attempting to fix code formatting. "
        "Code formatting should be done once comprehensively. We are keeping the "
        "most recent PR. See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "duplicate_dependencies": (
        "Closing as redundant. Multiple PRs are attempting to fix dependency issues. "
        "Dependencies should be resolved holistically. We are keeping the most "
        "comprehensive recent PR. See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "duplicate_refactoring": (
        "Closing as redundant. Multiple PRs are attempting major refactoring. "
        "Major refactoring should be done once in a coordinated manner. "
        "See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "merge_conflicts": (
        "Closing this merge conflict resolution PR. The original PR being "
        "resolved is itself stale and being closed. See PR_CLEANUP_ANALYSIS.md "
        "for details."
    ),
    "duplicate_logging": (
        "Closing as redundant. Multiple PRs are implementing logging improvements. "
        "We are keeping one comprehensive logging solution. "
        "See PR_CLEANUP_ANALYSIS.md for details."
    ),
    "wip_and_reports": (
        "Closing this PR as it is marked as WIP or is a report/task list rather "
        "than code changes. See PR_CLEANUP_ANALYSIS.md for details."
    ),
}


def get_github_token() -> str:
    """
    Get GitHub token from environment.

    The token must have permission to comment on and close pull requests for
    this repository. For most setups, a personal access token with the
    `repo` scope (or at least `public_repo` for public repositories only)
    is sufficient. When running in GitHub Actions, the built-in GITHUB_TOKEN
    is typically already configured with the required permissions.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print(
            "Please set it with: export GITHUB_TOKEN=your_token_here "
            "(token must allow commenting on and closing pull requests, "
            "e.g. a personal access token with the 'repo' scope)."
        )
        sys.exit(1)
    return token


def close_pr(pr_number: int, comment: str, token: str, dry_run: bool = True) -> bool:
    """
    Close a pull request and add a comment.

    In dry-run mode, prints the intended actions without making API calls. In execute mode, posts the comment and closes the pull request via the GitHub API.

    Parameters:
        dry_run (bool): If True, simulate the actions; if False, execute them

    Returns:
        bool: `true` if the operation succeeded (always in dry-run mode), `false` if an API call failed
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    pr_url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}"
    comment_url = (
        f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{pr_number}/comments"
    )

    if dry_run:
        print(f"[DRY RUN] Would close PR #{pr_number}")
        print(f"[DRY RUN] Would add comment: {comment[:100]}...")
        return True

    # Add comment
    try:
        comment_response = requests.post(
            comment_url, headers=headers, json={"body": comment}, timeout=30
        )
        if comment_response.status_code != 201:
            print(f"Error adding comment to PR #{pr_number}: {comment_response.text}")
            return False
    except Exception as e:
        print(f"Exception adding comment to PR #{pr_number}: {e}")
        return False

    # Close PR
    try:
        close_response = requests.patch(
            pr_url, headers=headers, json={"state": "closed"}, timeout=30
        )
        if close_response.status_code != 200:
            print(f"Error closing PR #{pr_number}: {close_response.text}")
            return False

        print(f"✓ Successfully closed PR #{pr_number}")
        return True
    except Exception as e:
        print(f"Exception closing PR #{pr_number}: {e}")
        return False


def close_prs_by_category(
    category: str, pr_numbers: list[int], token: str, dry_run: bool = True
) -> dict[str, int]:
    """
    Close a set of pull requests in a given category.

    Parameters:
        category (str): Category name used to select the closure comment message.
        pr_numbers (List[int]): PR numbers to close.
        token (str): GitHub API authentication token.
        dry_run (bool): If True, simulates the operation without making network requests.

    Returns:
        Dict[str, int]: Dictionary with "success" and "failed" keys indicating the count of closed and failed PRs.
    """
    message = CLOSURE_MESSAGES.get(category, CLOSURE_MESSAGES["september_prs"])

    print(f"\n{'='*80}")
    print(f"Processing category: {category}")
    print(f"PRs to close: {pr_numbers}")
    print(f"{'='*80}\n")

    results = {"success": 0, "failed": 0}

    for pr_number in pr_numbers:
        if close_pr(pr_number, message, token, dry_run):
            results["success"] += 1
        else:
            results["failed"] += 1

    return results


def main():
    """
    Parse arguments and close stale GitHub pull requests based on configuration.

    Operates in dry-run mode by default, showing what would be closed without
    making changes. Use --execute flag and confirm at the prompt to actually
    close PRs. Processes all configured PR categories or a single category
    via --category. Prints a summary of processed and closed PRs.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Close stale and redundant GitHub pull requests"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print actions without executing (default: True)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the PR closures (overrides --dry-run)",
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=[*STALE_PRS.keys(), "all"],
        help="Only process specific category (default: all)",
    )

    args = parser.parse_args()

    # Determine dry run mode
    dry_run = not args.execute

    if dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN MODE - No actual changes will be made")
        print("Use --execute flag to actually close PRs")
        print("=" * 80 + "\n")
    else:
        print("\n" + "=" * 80)
        print("EXECUTE MODE - PRs will actually be closed!")
        print("=" * 80 + "\n")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    # Get GitHub token
    token = get_github_token()

    # Process categories
    categories_to_process = (
        [args.category]
        if args.category and args.category != "all"
        else list(STALE_PRS.keys())
    )

    total_results = {"success": 0, "failed": 0}

    for category in categories_to_process:
        if category not in STALE_PRS:
            continue

        results = close_prs_by_category(category, STALE_PRS[category], token, dry_run)
        total_results["success"] += results["success"]
        total_results["failed"] += results["failed"]

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total PRs processed: {total_results['success'] + total_results['failed']}")
    print(f"Successfully closed: {total_results['success']}")
    print(f"Failed: {total_results['failed']}")

    if dry_run:
        print("\nThis was a dry run. Use --execute to actually close the PRs.")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
