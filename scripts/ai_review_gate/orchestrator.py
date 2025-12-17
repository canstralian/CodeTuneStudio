#!/usr/bin/env python3
"""
AI Code Review Gate - Main Orchestrator

Entry point for the AI code review process. Coordinates all components to:
1. Fetch PR changes from GitHub
2. Check context sufficiency
3. Perform code review
4. Format and post results
5. Set appropriate exit code

Exit codes:
- 0: Review passed
- 1: Review failed (violations found)
- 2: Review refused (insufficient context)
- 3: System error
"""

import sys
import os
import logging
import time
from datetime import datetime

from .github_api import GitHubClient
from .context import ContextGate
from .reviewer import CodeReviewer
from .formatter import OutputFormatter
from .diff_gen import DiffGenerator
from .types import ReviewResult, ReviewStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from environment variables."""
    config = {
        "pr_number": os.environ.get("PR_NUMBER"),
        "repo_name": os.environ.get("REPO_NAME"),
        "github_token": os.environ.get("GITHUB_TOKEN"),
        "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY"),
        "strict_mode": os.environ.get("STRICT_MODE", "false").lower() == "true",
        "fail_on_insufficient_context": os.environ.get(
            "FAIL_ON_INSUFFICIENT_CONTEXT", "true"
        ).lower()
        == "true",
        "max_files": int(os.environ.get("MAX_FILES_PER_PR", "50")),
        "max_lines": int(os.environ.get("MAX_LINES_PER_PR", "5000")),
    }

    # Validate required config
    required = ["pr_number", "repo_name", "github_token", "anthropic_api_key"]
    missing = [key for key in required if not config.get(key)]

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Convert PR number to int
    try:
        config["pr_number"] = int(config["pr_number"])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid PR_NUMBER: {config['pr_number']}")

    return config


def orchestrate_review():
    """
    Main orchestration function.

    Returns:
        Exit code (0-3)
    """
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("AI Code Review Gate - Starting Review")
    logger.info("=" * 80)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info(f"Configuration loaded: PR #{config['pr_number']}, strict_mode={config['strict_mode']}")

        # Initialize components
        logger.info("Initializing components...")
        github_client = GitHubClient(
            token=config["github_token"], repo_name=config["repo_name"]
        )
        context_gate = ContextGate(
            max_files=config["max_files"], max_lines=config["max_lines"]
        )
        reviewer = CodeReviewer(
            api_key=config["anthropic_api_key"], strict_mode=config["strict_mode"]
        )
        formatter = OutputFormatter()
        diff_generator = DiffGenerator()

        # Step 1: Fetch PR changes
        logger.info("Fetching PR changes from GitHub...")
        pr_changes = github_client.fetch_pr_changes(config["pr_number"])
        logger.info(
            f"Fetched PR: {pr_changes.file_count} files, {pr_changes.total_changes} lines changed"
        )

        # Step 2: Check context sufficiency
        logger.info("Checking context sufficiency...")
        context_check = context_gate.check_context_sufficiency(pr_changes)

        if not context_check.is_sufficient:
            logger.warning(f"Context insufficient: {context_check.reason}")

            # Create refused result
            result = ReviewResult(
                status=ReviewStatus.REFUSED,
                pr_changes=pr_changes,
                findings=[],
                context_check=context_check,
                execution_time=time.time() - start_time,
            )

            # Format and post refusal
            output = formatter.format_review_result(result)
            _write_output_files(output, result, formatter, diff_generator)

            github_client.post_review_comment(config["pr_number"], output)
            github_client.set_commit_status(
                pr_changes.head_sha, "failure", "Insufficient context for review"
            )

            # Return appropriate exit code
            if config["fail_on_insufficient_context"]:
                return 2  # Fail build
            else:
                return 0  # Allow build to continue

        # Step 3: Perform code review
        logger.info("Performing AI code review...")
        findings = reviewer.review_changes(pr_changes)
        logger.info(f"Review complete: {len(findings)} findings")

        # Determine status
        should_fail = reviewer.should_fail_build(findings)
        status = ReviewStatus.FAILED if should_fail else ReviewStatus.PASSED

        # Step 4: Create result
        result = ReviewResult(
            status=status,
            pr_changes=pr_changes,
            findings=findings,
            context_check=context_check,
            execution_time=time.time() - start_time,
        )

        # Step 5: Format output
        logger.info("Formatting review output...")
        output = formatter.format_review_result(result)

        # Step 6: Write output files (for artifacts)
        _write_output_files(output, result, formatter, diff_generator)

        # Step 7: Post to GitHub
        logger.info("Posting review to GitHub...")
        github_client.post_review_comment(config["pr_number"], output)

        # Set commit status
        if status == ReviewStatus.PASSED:
            github_client.set_commit_status(
                pr_changes.head_sha, "success", "All checks passed"
            )
        else:
            github_client.set_commit_status(
                pr_changes.head_sha,
                "failure",
                f"{result.summary['critical']} critical issue(s) found",
            )

        # Step 8: Return exit code
        logger.info("=" * 80)
        logger.info(f"Review completed: {status.value}")
        logger.info(f"Execution time: {result.execution_time:.2f}s")
        logger.info(f"Exit code: {result.exit_code}")
        logger.info("=" * 80)

        return result.exit_code

    except Exception as e:
        logger.error(f"Review failed with error: {e}", exc_info=True)

        # Try to post error message to GitHub
        try:
            error_message = f"""## 💥 AI Code Review - ERROR

**An unexpected error occurred during the review process.**

**Error:** {str(e)}

Please check the workflow logs for more details and try re-running the workflow.
"""
            if "github_client" in locals() and "config" in locals():
                github_client.post_review_comment(config["pr_number"], error_message)

        except Exception as post_error:
            logger.error(f"Failed to post error message: {post_error}")

        return 3  # System error


def _write_output_files(
    output: str, result: ReviewResult, formatter: OutputFormatter, diff_generator: DiffGenerator
):
    """
    Write output files for artifacts.

    Args:
        output: Formatted markdown output
        result: Review result
        formatter: Output formatter
        diff_generator: Diff generator
    """
    # Write markdown output
    with open("ai_review_output.md", "w") as f:
        f.write(output)
    logger.info("Wrote ai_review_output.md")

    # Write JSON summary
    json_output = formatter.format_summary_json(result)
    with open("ai_review_detailed.json", "w") as f:
        f.write(json_output)
    logger.info("Wrote ai_review_detailed.json")

    # Write patch file
    if result.findings:
        diff_generator.create_patch_file(result.findings, "ai_review_diffs.patch")


def main():
    """Main entry point."""
    try:
        exit_code = orchestrate_review()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Review interrupted by user")
        sys.exit(130)  # 128 + SIGINT
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(3)


if __name__ == "__main__":
    main()
