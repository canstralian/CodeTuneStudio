#!/usr/bin/env python3
"""
Automate Project Management

This script automates GitHub project board creation and management for the
CodeTuneStudio repository.

Usage:
    python -m automation.manage_project --create "Sprint 1"
    python -m automation.manage_project --list

Note: Advanced features like adding issues to projects require additional
      implementation. Use GitHub CLI (gh project) for comprehensive management.
"""

import argparse
import sys
from typing import Optional, Dict, Any, List

from automation.utils.github_api import GitHubAPIClient, get_github_token


class ProjectManager:
    """
    Handles automated project board creation and management.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize project manager.
        
        Args:
            token: GitHub personal access token
        """
        if token:
            self.client = GitHubAPIClient(token=token)
        else:
            self.client = None
    
    def create_project(
        self,
        name: str,
        description: str = "",
        org_level: bool = False,
        dry_run: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new project board.
        
        Args:
            name: Project name
            description: Project description
            org_level: Create at organization level vs repository level
            dry_run: If True, only print what would be created
            
        Returns:
            Project data dictionary if successful, None otherwise
        """
        if dry_run:
            print("=" * 80)
            print("DRY RUN - Project would be created with:")
            print("=" * 80)
            print(f"Name: {name}")
            print(f"Description: {description}")
            print(f"Level: {'Organization' if org_level else 'Repository'}")
            print("=" * 80)
            return None
        
        try:
            if not self.client:
                raise ValueError("GitHub API client not initialized. Token required.")
            
            project = self.client.create_project(
                name=name,
                body=description,
                org_level=org_level
            )
            
            print("=" * 80)
            print("✓ Project created successfully!")
            print("=" * 80)
            print(f"Name: {project['name']}")
            print(f"ID: {project['id']}")
            print(f"URL: {project['html_url']}")
            print("=" * 80)
            
            return project
            
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
    
    def list_projects(self, org_level: bool = False) -> List[Dict[str, Any]]:
        """
        List existing projects.
        
        Args:
            org_level: List organization-level projects
            
        Returns:
            List of project dictionaries (currently always empty - not implemented)
            
        Note:
            This is a stub implementation. Full project listing requires GraphQL API.
            For comprehensive project listing, use:
            - GitHub CLI: gh project list
            - GitHub GraphQL API: query with projects/projectsV2 fields
            - GitHub web interface
        """
        try:
            print("Listing projects...")
            print("Note: Full project listing is not yet implemented.")
            print("This feature requires GraphQL API for complete functionality.")
            print("For now, use GitHub CLI (gh project list) or web interface for project management.")
            return []
            
        except Exception as e:
            print(f"Error listing projects: {e}")
            return []


def main():
    """Main entry point for project management automation."""
    parser = argparse.ArgumentParser(
        description="Automate GitHub project management for CodeTuneStudio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new project
  %(prog)s --create "Sprint 1" --description "First sprint tasks"
  
  # Create organization-level project
  %(prog)s --create "Roadmap 2024" --org-level
  
  # Dry run to preview project
  %(prog)s --create "Test Project" --dry-run
  
  # List existing projects
  %(prog)s --list

Note: 
  For advanced project management features (adding cards, moving items, etc.),
  consider using the GitHub CLI (gh project) or GraphQL API directly.
  This script provides basic project creation functionality.
        """
    )
    
    parser.add_argument(
        "--create",
        dest="project_name",
        help="Create a new project with the given name"
    )
    
    parser.add_argument(
        "--description",
        default="",
        help="Project description"
    )
    
    parser.add_argument(
        "--org-level",
        action="store_true",
        help="Create project at organization level (requires org permissions)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing projects"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview project without creating it"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.project_name and not args.list:
        parser.error("One of --create or --list is required")
    
    try:
        token = None if args.dry_run else get_github_token()
        manager = ProjectManager(token=token)
        
        if args.list:
            projects = manager.list_projects(org_level=args.org_level)
            if projects:
                print(f"Found {len(projects)} projects")
            else:
                print("No projects found or listing not fully implemented")
                print("Use 'gh project list' for full project listing")
        
        if args.project_name:
            result = manager.create_project(
                name=args.project_name,
                description=args.description,
                org_level=args.org_level,
                dry_run=args.dry_run
            )
            sys.exit(0 if (args.dry_run or result) else 1)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
