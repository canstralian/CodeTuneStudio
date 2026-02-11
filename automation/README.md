# GitHub Automation Tools

Comprehensive automation scripts for GitHub operations including branch creation, issue management, and project board updates for the CodeTuneStudio repository.

## Features

- 🌿 **Branch Management**: Automated branch creation, switching, and deletion
- 🎫 **Issue Creation**: Template-based issue creation with labels and metadata
- 📋 **Project Management**: Project board creation and management
- 🔄 **API Integration**: GitHub REST API integration with rate limiting and error handling
- 🛡️ **Security**: Token-based authentication with environment variable support
- 🧪 **Testing**: Comprehensive unit tests for all functionality

## Prerequisites

- Python 3.8 or higher
- Git installed and configured
- GitHub Personal Access Token with appropriate permissions:
  - `repo` scope for full repository access
  - `public_repo` scope for public repositories only
  - `project` scope for project management (if creating projects)

## Installation

1. Install the CodeTuneStudio package (includes automation tools):
   ```bash
   pip install -e .
   ```

2. Set up your GitHub token:
   ```bash
   export GITHUB_TOKEN=your_github_personal_access_token
   ```
   
   Or add it to your `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your GITHUB_TOKEN
   ```

3. Verify installation:
   ```bash
   python -m automation.create_branch --help
   ```

## Usage

### Branch Creation

Create feature branches, bugfix branches, or any custom branches from a base branch.

**Basic usage:**
```bash
# Create a feature branch from main
python -m automation.create_branch feature/new-api

# Create a bugfix branch from develop
python -m automation.create_branch bugfix/critical-fix --base develop

# Create a branch without pushing to remote
python -m automation.create_branch feature/local-work --no-push

# Force recreate an existing branch
python -m automation.create_branch feature/restart --force
```

**Advanced usage:**
```bash
# Delete a branch (local only)
python -m automation.create_branch --delete old-feature

# Delete a branch including remote
python -m automation.create_branch --delete old-feature --delete-remote

# Switch to an existing branch
python -m automation.create_branch --switch feature/existing

# Specify repository path
python -m automation.create_branch feature/new --repo-path /path/to/repo
```

### Issue Creation

Create GitHub issues with templates, labels, and metadata.

**Basic usage:**
```bash
# Create a bug issue with template
python -m automation.create_issue \
  --template bug \
  --title "Login fails on mobile" \
  --description "Users cannot log in on mobile devices"

# Create issue with custom body
python -m automation.create_issue \
  --title "Update documentation" \
  --body "Documentation needs to be updated for new features"

# Create issue from a file
python -m automation.create_issue \
  --title "New Feature Request" \
  --from-file feature-request.md
```

**With labels and assignees:**
```bash
# Add labels
python -m automation.create_issue \
  --title "Fix failing tests" \
  --body "Some tests are failing in CI" \
  --labels bug,tests,urgent

# Assign to users
python -m automation.create_issue \
  --title "Review PR" \
  --body "Please review PR #123" \
  --assignees username1,username2

# Add to milestone
python -m automation.create_issue \
  --title "Sprint task" \
  --body "Complete feature X" \
  --milestone 5
```

**Templates:**
```bash
# List available templates
python -m automation.create_issue --list-templates

# Available templates:
# - bug: Bug report with reproduction steps
# - feature: Feature request with use cases
# - enhancement: Enhancement proposal
# - documentation: Documentation updates
# - task: Task with acceptance criteria

# Dry run to preview issue
python -m automation.create_issue \
  --template feature \
  --title "API v2" \
  --description "New API version" \
  --dry-run
```

### Project Management

Create and manage GitHub project boards.

**Basic usage:**
```bash
# Create a repository-level project
python -m automation.manage_project \
  --create "Sprint 1" \
  --description "First sprint tasks"

# Create organization-level project (requires org permissions)
python -m automation.manage_project \
  --create "Roadmap 2024" \
  --org-level

# Dry run to preview project
python -m automation.manage_project \
  --create "Test Project" \
  --dry-run

# List existing projects
python -m automation.manage_project --list
```

**Note:** For advanced project management features (adding cards, moving items, automation), use the GitHub CLI (`gh project`) or GraphQL API directly. This tool provides basic project creation functionality.

## Configuration

### Environment Variables

Configure automation tools via environment variables in `.env`:

```bash
# GitHub Personal Access Token (required)
GITHUB_TOKEN=your_github_token_here

# Repository configuration (optional)
GITHUB_REPO_OWNER=canstralian
GITHUB_REPO_NAME=CodeTuneStudio

# Auto-assign issues (optional)
AUTO_ASSIGN_ISSUES=false
DEFAULT_ISSUE_ASSIGNEE=username

# Enable verbose logging (optional)
AUTOMATION_VERBOSE=false
```

### Programmatic Usage

You can also use the automation tools programmatically in your Python scripts:

```python
from automation.utils.github_api import GitHubAPIClient
from automation.create_branch import BranchCreator
from automation.create_issue import IssueCreator
from automation.manage_project import ProjectManager

# Create GitHub API client
client = GitHubAPIClient(token="your_token")

# Create an issue
issue = client.create_issue(
    title="Bug Report",
    body="Description of the bug",
    labels=["bug", "urgent"]
)
print(f"Created issue #{issue['number']}")

# Create a branch
creator = BranchCreator(repo_path="/path/to/repo")
creator.create_branch(
    branch_name="feature/new-feature",
    base_branch="main",
    push=True
)

# Create an issue with template
issue_creator = IssueCreator(token="your_token")
issue = issue_creator.create_issue_from_template(
    title="New Feature",
    template="feature",
    description="Feature description",
    labels=["enhancement"]
)
```

## Testing

Run the automated tests:

```bash
# Run all automation tests
python -m pytest tests/test_automation.py -v

# Run with coverage
python -m pytest tests/test_automation.py --cov=automation --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_automation.py::TestGitHubAPIClient -v
```

## Examples

### Complete Workflow Example

Here's a complete example of creating a new feature:

```bash
# 1. Create a feature branch
python -m automation.create_branch feature/user-authentication

# 2. Create a tracking issue
python -m automation.create_issue \
  --template feature \
  --title "Implement user authentication" \
  --description "Add OAuth2 authentication for users" \
  --labels enhancement,security \
  --assignees yourusername

# 3. Create a project for tracking
python -m automation.manage_project \
  --create "Authentication Sprint" \
  --description "User authentication implementation"

# 4. Do your work...
# (write code, commit changes, etc.)

# 5. When done, can delete the branch if needed
python -m automation.create_branch --delete feature/user-authentication
```

### Batch Operations Example

Create multiple issues at once using a shell script:

```bash
#!/bin/bash
# create_sprint_issues.sh

# Array of issue titles
issues=(
  "Setup authentication framework"
  "Implement OAuth2 provider"
  "Add user registration flow"
  "Create login UI components"
  "Write authentication tests"
)

# Create each issue
for issue in "${issues[@]}"; do
  python -m automation.create_issue \
    --template task \
    --title "$issue" \
    --labels sprint-1,authentication \
    --milestone 1
done
```

### CI/CD Integration Example

Use automation tools in GitHub Actions:

```yaml
# .github/workflows/automation.yml
name: Automated Issue Creation

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  create-weekly-issue:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Create weekly planning issue
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m automation.create_issue \
            --template task \
            --title "Weekly Planning - $(date +%Y-%m-%d)" \
            --description "Planning for week of $(date +%Y-%m-%d)" \
            --labels planning,weekly
```

## API Reference

### GitHubAPIClient

Main client for GitHub API operations.

**Methods:**
- `create_issue(title, body, labels, assignees, milestone)`: Create a new issue
- `list_issues(state, labels, sort, direction, per_page)`: List repository issues
- `close_issue(issue_number, comment)`: Close an issue with optional comment
- `create_project(name, body, org_level)`: Create a project board
- `get_rate_limit()`: Get current API rate limit status
- `check_repo_access()`: Verify repository access

### BranchCreator

Handles branch creation and management.

**Methods:**
- `create_branch(branch_name, base_branch, push, force)`: Create a new branch
- `switch_branch(branch_name)`: Switch to existing branch
- `delete_branch(branch_name, force, delete_remote)`: Delete a branch
- `get_current_branch()`: Get current branch name
- `branch_exists(branch_name, check_remote)`: Check if branch exists

### IssueCreator

Handles issue creation with templates.

**Methods:**
- `create_issue(title, body, labels, assignees, milestone, dry_run)`: Create an issue
- `create_issue_from_template(title, template, description, ...)`: Create from template
- `create_issue_from_file(title, file_path, ...)`: Create from file
- `list_templates()`: Display available templates

### ProjectManager

Handles project board management.

**Methods:**
- `create_project(name, description, org_level, dry_run)`: Create a project
- `list_projects(org_level)`: List existing projects

## Troubleshooting

### Authentication Errors

**Problem:** `Error: GITHUB_TOKEN environment variable not set`

**Solution:** Set your GitHub token:
```bash
export GITHUB_TOKEN=your_token_here
```

### Permission Errors

**Problem:** `Failed to create issue: 403 - Forbidden`

**Solution:** Ensure your token has the required scopes:
- Check token permissions at https://github.com/settings/tokens
- Token needs `repo` scope for private repos or `public_repo` for public repos

### Branch Already Exists

**Problem:** `Error: Branch 'feature/x' already exists`

**Solution:** Use `--force` flag to recreate:
```bash
python -m automation.create_branch feature/x --force
```

### Rate Limiting

**Problem:** `Rate limited. Waiting 60 seconds...`

**Solution:** The tools automatically handle rate limiting by waiting. To avoid:
- Use fewer API calls
- Check rate limit status: `client.get_rate_limit()`
- Wait for rate limit reset

## Best Practices

1. **Use Templates**: Leverage issue templates for consistency
2. **Meaningful Names**: Use descriptive branch and issue names
3. **Dry Run First**: Use `--dry-run` to preview changes
4. **Label Everything**: Apply appropriate labels to issues
5. **Document Intent**: Include clear descriptions in issues and projects
6. **Version Control**: Keep automation scripts under version control
7. **Test First**: Run tests before deploying automation changes
8. **Secure Tokens**: Never commit tokens to version control

## Contributing

Contributions to improve automation tools are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

See the main [LICENSE](../LICENSE) file for details.

## Support

For issues or questions:
- Create an issue in the repository
- Check existing documentation
- Review the API reference above

## Changelog

### Version 1.0.0 (2024)
- Initial release
- Branch creation automation
- Issue creation with templates
- Project management basics
- Comprehensive testing
- Full documentation
