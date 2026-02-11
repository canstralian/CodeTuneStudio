# GitHub Automation Tools - Quick Reference

## Installation
```bash
export GITHUB_TOKEN=your_token_here
pip install -e .  # If not already installed
```

## Branch Operations

### Create Branch
```bash
# From main (default)
python -m automation.create_branch feature/my-feature

# From specific base
python -m automation.create_branch feature/my-feature --base develop

# Without pushing to remote
python -m automation.create_branch feature/my-feature --no-push
```

### Switch Branch
```bash
python -m automation.create_branch --switch existing-branch
```

### Delete Branch
```bash
# Local only
python -m automation.create_branch --delete old-branch

# Local and remote
python -m automation.create_branch --delete old-branch --delete-remote
```

## Issue Operations

### List Templates
```bash
python -m automation.create_issue --list-templates
```

### Create Issue
```bash
# With template
python -m automation.create_issue \
  --template bug \
  --title "Bug: Login fails" \
  --description "Cannot login on mobile" \
  --labels bug,urgent

# From file
python -m automation.create_issue \
  --title "Feature Request" \
  --from-file feature.md \
  --labels enhancement

# Simple issue
python -m automation.create_issue \
  --title "Update docs" \
  --body "Documentation needs updating" \
  --labels documentation
```

### Preview Issue (Dry Run)
```bash
python -m automation.create_issue \
  --template feature \
  --title "New API" \
  --dry-run
```

## Project Operations

### Create Project
```bash
# Repository level
python -m automation.manage_project \
  --create "Sprint 1" \
  --description "First sprint tasks"

# Organization level
python -m automation.manage_project \
  --create "Roadmap 2024" \
  --org-level
```

### Preview Project (Dry Run)
```bash
python -m automation.manage_project \
  --create "Test Project" \
  --dry-run
```

## Common Workflows

### Start New Feature
```bash
# 1. Create branch
python -m automation.create_branch feature/user-auth

# 2. Create tracking issue
python -m automation.create_issue \
  --template feature \
  --title "Implement user authentication" \
  --labels enhancement,security

# 3. Do your work...
# 4. Create PR (use gh cli or web UI)
```

### Report Bug
```bash
python -m automation.create_issue \
  --template bug \
  --title "Login fails on Safari" \
  --description "Users cannot login using Safari browser" \
  --labels bug,browser-compatibility,high-priority
```

### Plan Sprint
```bash
# 1. Create project
python -m automation.manage_project \
  --create "Sprint $(date +%Y-%m-%d)" \
  --description "Sprint starting $(date +%Y-%m-%d)"

# 2. Create tasks
python -m automation.create_issue --template task --title "Task 1" --labels sprint
python -m automation.create_issue --template task --title "Task 2" --labels sprint
```

## Tips

- Use `--dry-run` to preview before creating
- Use `--help` on any command for full options
- Templates ensure consistent issue formatting
- All operations can be scripted for automation
- Check `automation/README.md` for full documentation

## Environment Variables

```bash
# Required for real operations
GITHUB_TOKEN=your_github_token

# Optional configuration
GITHUB_REPO_OWNER=canstralian
GITHUB_REPO_NAME=CodeTuneStudio
AUTO_ASSIGN_ISSUES=false
DEFAULT_ISSUE_ASSIGNEE=username
AUTOMATION_VERBOSE=false
```

## Getting Help

```bash
python -m automation.create_branch --help
python -m automation.create_issue --help
python -m automation.manage_project --help
```

## Full Documentation

- [Complete Guide](automation/README.md)
- [Implementation Summary](AUTOMATION_IMPLEMENTATION_SUMMARY.md)
- [Main README](README.md)
