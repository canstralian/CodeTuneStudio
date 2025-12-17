"""
GitHub API Integration - Fetches PR data and posts review results.

Handles:
- Fetching PR changes and metadata
- Posting review comments
- Setting commit status checks
- Adding file annotations
"""

import logging
import os
from typing import Optional, List
from datetime import datetime
from github import Github, GithubException
from .types import PRChanges, FileChange, ReviewResult

logger = logging.getLogger(__name__)


class GitHubClient:
    """
    GitHub API client for PR review operations.
    """

    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize GitHub client.

        Args:
            token: GitHub token (reads from env if not provided)
            repo_name: Repository name in format "owner/repo"
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN is required")

        self.repo_name = repo_name or os.environ.get("REPO_NAME")
        if not self.repo_name:
            raise ValueError("REPO_NAME is required (format: owner/repo)")

        self.client = Github(self.token)
        self.repo = self.client.get_repo(self.repo_name)

        logger.info(f"Initialized GitHub client for {self.repo_name}")

    def fetch_pr_changes(self, pr_number: int) -> PRChanges:
        """
        Fetch PR changes and metadata.

        Args:
            pr_number: Pull request number

        Returns:
            PR changes object
        """
        logger.info(f"Fetching PR #{pr_number}")

        try:
            pr = self.repo.get_pull(pr_number)

            # Collect file changes
            files = []
            for file in pr.get_files():
                file_change = FileChange(
                    filename=file.filename,
                    status=file.status,
                    additions=file.additions,
                    deletions=file.deletions,
                    changes=file.changes,
                    patch=file.patch,
                    previous_filename=file.previous_filename,
                    raw_url=file.raw_url,
                )
                files.append(file_change)

            # Create PR changes object
            changes = PRChanges(
                pr_number=pr.number,
                title=pr.title,
                description=pr.body or "",
                base_ref=pr.base.ref,
                head_ref=pr.head.ref,
                base_sha=pr.base.sha,
                head_sha=pr.head.sha,
                files=files,
                total_additions=pr.additions,
                total_deletions=pr.deletions,
                total_changes=pr.additions + pr.deletions,
                file_count=pr.changed_files,
                author=pr.user.login,
                created_at=pr.created_at,
                updated_at=pr.updated_at,
            )

            logger.info(
                f"Fetched PR #{pr_number}: {changes.file_count} files, "
                f"{changes.total_changes} lines changed"
            )

            return changes

        except GithubException as e:
            logger.error(f"Failed to fetch PR #{pr_number}: {e}")
            raise

    def post_review_comment(self, pr_number: int, body: str) -> None:
        """
        Post review comment to PR.

        Args:
            pr_number: Pull request number
            body: Comment body (markdown)
        """
        logger.info(f"Posting review comment to PR #{pr_number}")

        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(body)
            logger.info("Review comment posted successfully")

        except GithubException as e:
            logger.error(f"Failed to post review comment: {e}")
            raise

    def set_commit_status(
        self,
        commit_sha: str,
        state: str,
        description: str,
        context: str = "AI Code Review Gate",
    ) -> None:
        """
        Set commit status check.

        Args:
            commit_sha: Commit SHA to update
            state: Status state (pending, success, failure, error)
            description: Status description
            context: Status context name
        """
        logger.info(f"Setting commit status for {commit_sha[:7]}: {state}")

        try:
            commit = self.repo.get_commit(commit_sha)
            commit.create_status(
                state=state, description=description, context=context
            )
            logger.info("Commit status updated successfully")

        except GithubException as e:
            logger.error(f"Failed to set commit status: {e}")
            raise

    def add_review_with_comments(
        self, pr_number: int, result: ReviewResult, body: str
    ) -> None:
        """
        Submit a review with inline comments for each finding.

        Args:
            pr_number: Pull request number
            result: Review result with findings
            body: Overall review body
        """
        logger.info(f"Submitting review with inline comments to PR #{pr_number}")

        try:
            pr = self.repo.get_pull(pr_number)

            # Build review comments for each finding
            comments = []
            for finding in result.findings:
                comment = {
                    "path": finding.violation.file_path,
                    "line": finding.violation.line_start,
                    "body": self._format_inline_comment(finding),
                }
                comments.append(comment)

            # Determine review event
            if result.has_critical_issues:
                event = "REQUEST_CHANGES"
            else:
                event = "COMMENT"

            # Create review
            if comments:
                pr.create_review(body=body, event=event, comments=comments)
            else:
                # No inline comments, just post as regular comment
                pr.create_issue_comment(body)

            logger.info("Review submitted successfully")

        except GithubException as e:
            logger.error(f"Failed to submit review: {e}")
            # Fall back to regular comment
            logger.info("Falling back to regular comment")
            self.post_review_comment(pr_number, body)

    def _format_inline_comment(self, finding) -> str:
        """
        Format finding as inline comment.

        Args:
            finding: Finding object

        Returns:
            Formatted comment
        """
        severity_emoji = "🚨" if finding.severity.value == "critical" else "⚠️"

        comment = f"""{severity_emoji} **{finding.title}**

**{finding.description}**

{finding.explanation}
"""

        if finding.suggested_code:
            comment += f"""
**Suggested fix:**
```python
{finding.suggested_code}
```
"""

        if finding.documentation_url:
            comment += f"\n📚 [Learn more]({finding.documentation_url})"

        return comment

    def update_check_run(
        self,
        check_run_id: int,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[dict] = None,
    ) -> None:
        """
        Update GitHub check run.

        Args:
            check_run_id: Check run ID
            status: Status (queued, in_progress, completed)
            conclusion: Conclusion if completed (success, failure, cancelled, etc.)
            output: Output details
        """
        logger.info(f"Updating check run {check_run_id}: {status}")

        try:
            # Note: This requires the checks API which needs special permissions
            # For now, we'll use commit status instead
            pass

        except Exception as e:
            logger.warning(f"Failed to update check run: {e}")

    def get_pr_number_from_event(self) -> Optional[int]:
        """
        Extract PR number from GitHub Actions event context.

        Returns:
            PR number or None
        """
        pr_number = os.environ.get("PR_NUMBER")
        if pr_number:
            try:
                return int(pr_number)
            except ValueError:
                logger.error(f"Invalid PR_NUMBER: {pr_number}")

        return None
