#!/usr/bin/env python3
"""
Unit tests for GitHub automation tools.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.utils.github_api import GitHubAPIClient, get_github_token
from automation.create_branch import BranchCreator
from automation.create_issue import IssueCreator, TEMPLATES
from automation.manage_project import ProjectManager
from automation.config import get_config, validate_config


class TestGitHubAPIClient(unittest.TestCase):
    """Test cases for GitHubAPIClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.token = "test_token_123"
        self.client = GitHubAPIClient(token=self.token)
    
    def test_client_initialization(self):
        """Test client initializes with correct values."""
        self.assertEqual(self.client.token, self.token)
        self.assertEqual(self.client.owner, "canstralian")
        self.assertEqual(self.client.repo, "CodeTuneStudio")
        self.assertIn("Authorization", self.client.headers)
        self.assertEqual(
            self.client.headers["Authorization"],
            f"Bearer {self.token}"
        )
    
    def test_client_initialization_no_token(self):
        """Test client raises error when no token provided."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                GitHubAPIClient()
    
    def test_client_initialization_from_env(self):
        """Test client reads token from environment."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            client = GitHubAPIClient()
            self.assertEqual(client.token, "env_token")
    
    @patch("automation.utils.github_api.requests.request")
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        response = self.client._make_request("GET", "/test")
        
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once()
    
    @patch("automation.utils.github_api.requests.request")
    @patch("automation.utils.github_api.time.sleep")
    def test_make_request_rate_limit(self, mock_sleep, mock_request):
        """Test rate limit handling."""
        # First call returns rate limit, second succeeds
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "5"}
        
        success_response = Mock()
        success_response.status_code = 200
        
        mock_request.side_effect = [rate_limit_response, success_response]
        
        response = self.client._make_request("GET", "/test")
        
        self.assertEqual(response.status_code, 200)
        mock_sleep.assert_called_once_with(5)
    
    @patch("automation.utils.github_api.requests.request")
    def test_create_issue(self, mock_request):
        """Test issue creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 123,
            "html_url": "https://github.com/test/issue/123",
            "title": "Test Issue"
        }
        mock_request.return_value = mock_response
        
        result = self.client.create_issue(
            title="Test Issue",
            body="Test body",
            labels=["bug"]
        )
        
        self.assertEqual(result["number"], 123)
        self.assertIn("html_url", result)
    
    @patch("automation.utils.github_api.requests.request")
    def test_list_issues(self, mock_request):
        """Test issue listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"number": 1, "title": "Issue 1"},
            {"number": 2, "title": "Issue 2"}
        ]
        mock_request.return_value = mock_response
        
        result = self.client.list_issues(state="open")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["number"], 1)
    
    @patch("automation.utils.github_api.requests.request")
    def test_check_repo_access(self, mock_request):
        """Test repository access check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = self.client.check_repo_access()
        
        self.assertTrue(result)


class TestBranchCreator(unittest.TestCase):
    """Test cases for BranchCreator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.creator = BranchCreator(repo_path=self.test_repo_path)
    
    def test_initialization(self):
        """Test creator initializes with valid repo."""
        self.assertEqual(str(self.creator.repo_path), self.test_repo_path)
    
    def test_initialization_invalid_repo(self):
        """Test creator raises error for invalid repo."""
        with self.assertRaises(ValueError):
            BranchCreator(repo_path="/tmp/not_a_repo")
    
    @patch("automation.create_branch.subprocess.run")
    def test_run_git_command(self, mock_run):
        """Test Git command execution."""
        mock_run.return_value = Mock(stdout="test output", returncode=0)
        
        result = self.creator.run_git_command("status")
        
        mock_run.assert_called_once()
        self.assertIn("git", mock_run.call_args[0][0])
        self.assertEqual(result.stdout, "test output")
    
    @patch("automation.create_branch.subprocess.run")
    def test_get_current_branch(self, mock_run):
        """Test getting current branch name."""
        mock_run.return_value = Mock(stdout="main\n", returncode=0)
        
        branch = self.creator.get_current_branch()
        
        self.assertEqual(branch, "main")


class TestIssueCreator(unittest.TestCase):
    """Test cases for IssueCreator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.token = "test_token"
        with patch("automation.create_issue.GitHubAPIClient"):
            self.creator = IssueCreator(token=self.token)
    
    def test_templates_exist(self):
        """Test that all expected templates are defined."""
        expected_templates = ["bug", "feature", "enhancement", "documentation", "task"]
        for template in expected_templates:
            self.assertIn(template, TEMPLATES)
    
    def test_create_issue_from_template(self):
        """Test creating issue from template."""
        self.creator.client.create_issue = Mock(return_value={
            "number": 123,
            "html_url": "https://github.com/test",
            "title": "Test",
            "state": "open"
        })
        
        result = self.creator.create_issue_from_template(
            title="Test Issue",
            template="bug",
            description="Test description"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result["number"], 123)
    
    def test_create_issue_invalid_template(self):
        """Test creating issue with invalid template."""
        result = self.creator.create_issue_from_template(
            title="Test",
            template="invalid_template",
            description="Test"
        )
        
        self.assertIsNone(result)
    
    def test_create_issue_dry_run(self):
        """Test dry run mode doesn't create issue."""
        result = self.creator.create_issue(
            title="Test",
            body="Test body",
            dry_run=True
        )
        
        self.assertIsNone(result)


class TestProjectManager(unittest.TestCase):
    """Test cases for ProjectManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.token = "test_token"
        with patch("automation.manage_project.GitHubAPIClient"):
            self.manager = ProjectManager(token=self.token)
    
    def test_create_project_dry_run(self):
        """Test dry run mode doesn't create project."""
        result = self.manager.create_project(
            name="Test Project",
            description="Test",
            dry_run=True
        )
        
        self.assertIsNone(result)
    
    def test_create_project(self):
        """Test creating project."""
        self.manager.client.create_project = Mock(return_value={
            "id": 456,
            "name": "Test Project",
            "html_url": "https://github.com/test"
        })
        
        result = self.manager.create_project(
            name="Test Project",
            description="Test description"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 456)


class TestConfig(unittest.TestCase):
    """Test cases for configuration."""
    
    def test_get_config(self):
        """Test getting configuration."""
        config = get_config()
        
        self.assertIsInstance(config, dict)
        self.assertIn("repo_owner", config)
        self.assertIn("repo_name", config)
        self.assertIn("default_base_branch", config)
    
    def test_validate_config(self):
        """Test configuration validation."""
        result = validate_config()
        
        # Should be valid with default settings
        self.assertTrue(result)


class TestGetGitHubToken(unittest.TestCase):
    """Test cases for get_github_token function."""
    
    def test_get_token_from_env(self):
        """Test getting token from environment."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            token = get_github_token()
            self.assertEqual(token, "test_token")
    
    def test_get_token_not_set(self):
        """Test error when token not set."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                get_github_token()


if __name__ == "__main__":
    unittest.main()
