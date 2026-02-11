#!/usr/bin/env python3
"""
GitHub API Client for Automation Scripts

Provides a centralized client for interacting with GitHub's REST and GraphQL APIs.
Handles authentication, rate limiting, and common error scenarios.
"""

import os
import sys
import time
from typing import Dict, List, Optional, Any
import requests


class GitHubAPIClient:
    """
    Client for interacting with GitHub API.
    
    This client provides methods for common GitHub operations and handles
    authentication, rate limiting, and error responses consistently.
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        owner: str = "canstralian",
        repo: str = "CodeTuneStudio"
    ):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token. If None, reads from GITHUB_TOKEN env var.
            owner: Repository owner (username or organization)
            repo: Repository name
            
        Raises:
            ValueError: If no token is provided or found in environment
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass token parameter."
            )
        
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> requests.Response:
        """
        Make an API request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (without base URL)
            data: JSON data for request body
            params: Query parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                return response
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise requests.RequestException("Max retries exceeded")
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue in the repository.
        
        Args:
            title: Issue title
            body: Issue description/body
            labels: List of label names to apply
            assignees: List of usernames to assign
            milestone: Milestone number to associate with
            
        Returns:
            Dictionary containing issue data including 'html_url' and 'number'
            
        Raises:
            requests.RequestException: If issue creation fails
        """
        endpoint = f"/repos/{self.owner}/{self.repo}/issues"
        data = {
            "title": title,
            "body": body,
        }
        
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone
        
        response = self._make_request("POST", endpoint, data=data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise requests.RequestException(
                f"Failed to create issue: {response.status_code} - {response.text}"
            )
    
    def list_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        sort: str = "created",
        direction: str = "desc",
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        List issues in the repository.
        
        Args:
            state: Issue state filter ('open', 'closed', 'all')
            labels: Filter by label names
            sort: Sort field ('created', 'updated', 'comments')
            direction: Sort direction ('asc', 'desc')
            per_page: Results per page (max 100)
            
        Returns:
            List of issue dictionaries
        """
        endpoint = f"/repos/{self.owner}/{self.repo}/issues"
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100)
        }
        
        if labels:
            params["labels"] = ",".join(labels)
        
        response = self._make_request("GET", endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.RequestException(
                f"Failed to list issues: {response.status_code} - {response.text}"
            )
    
    def close_issue(
        self,
        issue_number: int,
        comment: Optional[str] = None
    ) -> bool:
        """
        Close an issue, optionally adding a comment.
        
        Args:
            issue_number: Issue number to close
            comment: Optional comment to add before closing
            
        Returns:
            True if successful
            
        Raises:
            requests.RequestException: If operation fails
        """
        # Add comment if provided
        if comment:
            comment_endpoint = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
            comment_response = self._make_request(
                "POST",
                comment_endpoint,
                data={"body": comment}
            )
            if comment_response.status_code != 201:
                raise requests.RequestException(
                    f"Failed to add comment: {comment_response.status_code}"
                )
        
        # Close the issue
        endpoint = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        response = self._make_request(
            "PATCH",
            endpoint,
            data={"state": "closed"}
        )
        
        if response.status_code == 200:
            return True
        else:
            raise requests.RequestException(
                f"Failed to close issue: {response.status_code} - {response.text}"
            )
    
    def create_project(
        self,
        name: str,
        body: str = "",
        org_level: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new project board.
        
        Args:
            name: Project name
            body: Project description
            org_level: If True, create at organization level, else repository level
            
        Returns:
            Dictionary containing project data
            
        Note:
            This uses the projects preview API which may change.
        """
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.inertia-preview+json"
        
        if org_level:
            endpoint = f"/orgs/{self.owner}/projects"
        else:
            endpoint = f"/repos/{self.owner}/{self.repo}/projects"
        
        data = {
            "name": name,
            "body": body
        }
        
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise requests.RequestException(
                f"Failed to create project: {response.status_code} - {response.text}"
            )
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        response = self._make_request("GET", "/rate_limit")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.RequestException(
                f"Failed to get rate limit: {response.status_code}"
            )
    
    def check_repo_access(self) -> bool:
        """
        Check if the client has access to the configured repository.
        
        Returns:
            True if repository is accessible, False otherwise
        """
        endpoint = f"/repos/{self.owner}/{self.repo}"
        try:
            response = self._make_request("GET", endpoint)
            return response.status_code == 200
        except requests.RequestException:
            return False


def get_github_token() -> str:
    """
    Get GitHub token from environment with helpful error message.
    
    Returns:
        GitHub token string
        
    Raises:
        SystemExit: If token is not found
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print()
        print("To use GitHub automation tools, you need a Personal Access Token with:")
        print("  - repo scope (for full repository access)")
        print("  - public_repo scope (for public repositories only)")
        print()
        print("Set the token with:")
        print("  export GITHUB_TOKEN=your_token_here")
        print()
        print("Or add it to your .env file:")
        print("  GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    return token
