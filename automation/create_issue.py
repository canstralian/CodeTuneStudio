#!/usr/bin/env python3
"""
Automate Issue Creation

This script automates the creation of GitHub issues with templates, labels,
and metadata for the CodeTuneStudio repository.

Usage:
    python -m automation.create_issue --title "Bug: Fix login" --body "Details..."
    python -m automation.create_issue --template bug --title "Critical bug"
    python -m automation.create_issue --from-file issue.md --labels bug,urgent
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from automation.utils.github_api import GitHubAPIClient, get_github_token


# Issue templates
TEMPLATES = {
    "bug": """## Bug Description
{description}

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior


## Actual Behavior


## Environment
- OS: 
- Python Version: 
- CodeTuneStudio Version: 

## Additional Context

""",
    
    "feature": """## Feature Request
{description}

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other approaches did you consider?

## Additional Context

""",
    
    "enhancement": """## Enhancement Description
{description}

## Current Behavior


## Proposed Enhancement


## Benefits
- 
- 

## Implementation Considerations

""",
    
    "documentation": """## Documentation Issue
{description}

## Location
Where is the documentation that needs updating?

## Proposed Changes


## Why This Matters

""",
    
    "task": """## Task Description
{description}

## Acceptance Criteria
- [ ] 
- [ ] 
- [ ] 

## Dependencies


## Estimated Effort

"""
}


class IssueCreator:
    """
    Handles automated issue creation with templates and metadata.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize issue creator.
        
        Args:
            token: GitHub personal access token
        """
        if token:
            self.client = GitHubAPIClient(token=token)
        else:
            self.client = None
    
    def create_issue_from_template(
        self,
        title: str,
        template: str,
        description: str = "",
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
        dry_run: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create an issue using a predefined template.
        
        Args:
            title: Issue title
            template: Template name (bug, feature, enhancement, etc.)
            description: Description to fill in template
            labels: List of labels to apply
            assignees: List of usernames to assign
            milestone: Milestone number
            dry_run: If True, only print what would be created
            
        Returns:
            Issue data dictionary if successful, None otherwise
        """
        if template not in TEMPLATES:
            print(f"Error: Unknown template '{template}'")
            print(f"Available templates: {', '.join(TEMPLATES.keys())}")
            return None
        
        # Generate body from template
        body = TEMPLATES[template].format(description=description)
        
        return self.create_issue(
            title=title,
            body=body,
            labels=labels,
            assignees=assignees,
            milestone=milestone,
            dry_run=dry_run
        )
    
    def create_issue_from_file(
        self,
        title: str,
        file_path: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
        dry_run: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create an issue with body content from a file.
        
        Args:
            title: Issue title
            file_path: Path to file containing issue body
            labels: List of labels to apply
            assignees: List of usernames to assign
            milestone: Milestone number
            dry_run: If True, only print what would be created
            
        Returns:
            Issue data dictionary if successful, None otherwise
        """
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}")
            return None
        
        try:
            body = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
        
        return self.create_issue(
            title=title,
            body=body,
            labels=labels,
            assignees=assignees,
            milestone=milestone,
            dry_run=dry_run
        )
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
        dry_run: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a GitHub issue.
        
        Args:
            title: Issue title
            body: Issue body/description
            labels: List of labels to apply
            assignees: List of usernames to assign
            milestone: Milestone number
            dry_run: If True, only print what would be created
            
        Returns:
            Issue data dictionary if successful, None otherwise
        """
        if dry_run:
            print("=" * 80)
            print("DRY RUN - Issue would be created with:")
            print("=" * 80)
            print(f"Title: {title}")
            print(f"Labels: {', '.join(labels) if labels else 'None'}")
            print(f"Assignees: {', '.join(assignees) if assignees else 'None'}")
            print(f"Milestone: {milestone or 'None'}")
            print("-" * 80)
            print("Body:")
            print(body)
            print("=" * 80)
            return None
        
        try:
            if not self.client:
                raise ValueError("GitHub API client not initialized. Token required.")
            
            issue = self.client.create_issue(
                title=title,
                body=body,
                labels=labels,
                assignees=assignees,
                milestone=milestone
            )
            
            print("=" * 80)
            print("✓ Issue created successfully!")
            print("=" * 80)
            print(f"Number: #{issue['number']}")
            print(f"Title: {issue['title']}")
            print(f"URL: {issue['html_url']}")
            print(f"State: {issue['state']}")
            if issue.get('labels'):
                print(f"Labels: {', '.join(l['name'] for l in issue['labels'])}")
            print("=" * 80)
            
            return issue
            
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
    
    def list_templates(self) -> None:
        """Display available issue templates."""
        print("Available Issue Templates:")
        print("=" * 80)
        for name, template in TEMPLATES.items():
            print(f"\n{name}:")
            print("-" * 40)
            # Show first few lines of template
            lines = template.split('\n')[:5]
            for line in lines:
                print(f"  {line}")
            print("  ...")
        print("=" * 80)


def main():
    """Main entry point for issue creation automation."""
    parser = argparse.ArgumentParser(
        description="Automate GitHub issue creation for CodeTuneStudio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a bug issue with template
  %(prog)s --template bug --title "Login fails" --description "Users can't log in"
  
  # Create issue from a file
  %(prog)s --title "New Feature" --from-file feature.md
  
  # Create issue with labels and assignees
  %(prog)s --title "Fix tests" --body "Some tests failing" --labels bug,tests --assignees username
  
  # Dry run to preview issue
  %(prog)s --template feature --title "API v2" --dry-run
  
  # List available templates
  %(prog)s --list-templates
        """
    )
    
    parser.add_argument(
        "--title",
        help="Issue title"
    )
    
    parser.add_argument(
        "--body",
        help="Issue body/description"
    )
    
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        help="Use a predefined template"
    )
    
    parser.add_argument(
        "--description",
        help="Description to fill in template (used with --template)"
    )
    
    parser.add_argument(
        "--from-file",
        dest="file_path",
        help="Read issue body from a file"
    )
    
    parser.add_argument(
        "--labels",
        help="Comma-separated list of labels to apply"
    )
    
    parser.add_argument(
        "--assignees",
        help="Comma-separated list of usernames to assign"
    )
    
    parser.add_argument(
        "--milestone",
        type=int,
        help="Milestone number to associate with"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview issue without creating it"
    )
    
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available issue templates"
    )
    
    args = parser.parse_args()
    
    # Handle list templates (doesn't require token)
    if args.list_templates:
        creator = IssueCreator(token=None)
        creator.list_templates()
        sys.exit(0)
    
    # Validate required arguments
    if not args.title:
        parser.error("--title is required (unless using --list-templates)")
    
    if not args.body and not args.template and not args.file_path:
        parser.error("One of --body, --template, or --from-file is required")
    
    # Parse labels and assignees
    labels = args.labels.split(",") if args.labels else None
    assignees = args.assignees.split(",") if args.assignees else None
    
    try:
        token = None if args.dry_run else get_github_token()
        creator = IssueCreator(token=token)
        
        # Create issue based on input method
        if args.file_path:
            result = creator.create_issue_from_file(
                title=args.title,
                file_path=args.file_path,
                labels=labels,
                assignees=assignees,
                milestone=args.milestone,
                dry_run=args.dry_run
            )
        elif args.template:
            result = creator.create_issue_from_template(
                title=args.title,
                template=args.template,
                description=args.description or "",
                labels=labels,
                assignees=assignees,
                milestone=args.milestone,
                dry_run=args.dry_run
            )
        else:
            result = creator.create_issue(
                title=args.title,
                body=args.body,
                labels=labels,
                assignees=assignees,
                milestone=args.milestone,
                dry_run=args.dry_run
            )
        
        sys.exit(0 if (args.dry_run or result) else 1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
