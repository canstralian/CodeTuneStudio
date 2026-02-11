#!/usr/bin/env python3
"""
Automate Branch Creation

This script automates the creation and management of Git branches for the
CodeTuneStudio repository. It supports both local and remote branch creation
with various options for base branches and automatic push.

Usage:
    python -m automation.create_branch feature/my-new-feature
    python -m automation.create_branch bugfix/critical-fix --base develop
    python -m automation.create_branch feature/api-update --no-push
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


class BranchCreator:
    """
    Handles automated branch creation and management.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize branch creator.
        
        Args:
            repo_path: Path to Git repository. Defaults to current directory.
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        
        # Verify this is a Git repository
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a Git repository: {self.repo_path}")
    
    def run_git_command(self, *args: str) -> subprocess.CompletedProcess:
        """
        Run a Git command in the repository.
        
        Args:
            *args: Git command arguments
            
        Returns:
            CompletedProcess instance
            
        Raises:
            subprocess.CalledProcessError: If Git command fails
        """
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            raise
    
    def fetch_latest(self, remote: str = "origin") -> None:
        """
        Fetch latest changes from remote.
        
        Args:
            remote: Remote name (default: origin)
        """
        print(f"Fetching latest changes from {remote}...")
        self.run_git_command("fetch", remote)
        print("✓ Fetch complete")
    
    def get_current_branch(self) -> str:
        """
        Get the name of the current branch.
        
        Returns:
            Current branch name
        """
        result = self.run_git_command("branch", "--show-current")
        return result.stdout.strip()
    
    def branch_exists(self, branch_name: str, check_remote: bool = False) -> bool:
        """
        Check if a branch exists locally or remotely.
        
        Args:
            branch_name: Name of the branch to check
            check_remote: If True, check remote branches
            
        Returns:
            True if branch exists, False otherwise
        """
        try:
            if check_remote:
                self.run_git_command("ls-remote", "--heads", "origin", branch_name)
            else:
                self.run_git_command("rev-parse", "--verify", branch_name)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_branch(
        self,
        branch_name: str,
        base_branch: str = "main",
        push: bool = True,
        force: bool = False
    ) -> bool:
        """
        Create a new branch from a base branch.
        
        Args:
            branch_name: Name of the new branch
            base_branch: Base branch to create from (default: main)
            push: Whether to push the branch to remote (default: True)
            force: Force creation even if branch exists (default: False)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if branch already exists
            if self.branch_exists(branch_name) and not force:
                print(f"Error: Branch '{branch_name}' already exists locally.")
                print("Use --force to recreate the branch.")
                return False
            
            if self.branch_exists(branch_name, check_remote=True) and not force:
                print(f"Error: Branch '{branch_name}' already exists on remote.")
                print("Use --force to recreate the branch.")
                return False
            
            # Fetch latest to ensure base branch is up-to-date
            self.fetch_latest()
            
            # Delete existing branch if forcing
            if force and self.branch_exists(branch_name):
                print(f"Deleting existing local branch '{branch_name}'...")
                self.run_git_command("branch", "-D", branch_name)
            
            # Create and checkout new branch from base
            print(f"Creating branch '{branch_name}' from 'origin/{base_branch}'...")
            self.run_git_command(
                "checkout",
                "-b",
                branch_name,
                f"origin/{base_branch}"
            )
            print(f"✓ Branch '{branch_name}' created and checked out")
            
            # Push to remote if requested
            if push:
                print(f"Pushing branch '{branch_name}' to origin...")
                if force:
                    self.run_git_command("push", "-f", "-u", "origin", branch_name)
                else:
                    self.run_git_command("push", "-u", "origin", branch_name)
                print(f"✓ Branch '{branch_name}' pushed to origin")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating branch: {e}")
            return False
    
    def switch_branch(self, branch_name: str) -> bool:
        """
        Switch to an existing branch.
        
        Args:
            branch_name: Name of the branch to switch to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Switching to branch '{branch_name}'...")
            self.run_git_command("checkout", branch_name)
            print(f"✓ Switched to branch '{branch_name}'")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error switching branch: {e}")
            return False
    
    def delete_branch(
        self,
        branch_name: str,
        force: bool = False,
        delete_remote: bool = False
    ) -> bool:
        """
        Delete a branch locally and optionally on remote.
        
        Args:
            branch_name: Name of the branch to delete
            force: Force deletion even if not fully merged
            delete_remote: Also delete the branch from remote
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if it's the current branch
            current = self.get_current_branch()
            if current == branch_name:
                print(f"Error: Cannot delete the current branch '{branch_name}'")
                print("Switch to another branch first.")
                return False
            
            # Delete local branch
            delete_flag = "-D" if force else "-d"
            print(f"Deleting local branch '{branch_name}'...")
            self.run_git_command("branch", delete_flag, branch_name)
            print(f"✓ Local branch '{branch_name}' deleted")
            
            # Delete remote branch if requested
            if delete_remote:
                print(f"Deleting remote branch '{branch_name}'...")
                self.run_git_command("push", "origin", "--delete", branch_name)
                print(f"✓ Remote branch '{branch_name}' deleted")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error deleting branch: {e}")
            return False


def main():
    """Main entry point for branch creation automation."""
    parser = argparse.ArgumentParser(
        description="Automate Git branch creation for CodeTuneStudio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a feature branch from main
  %(prog)s feature/new-api
  
  # Create a bugfix branch from develop
  %(prog)s bugfix/critical-fix --base develop
  
  # Create a branch without pushing to remote
  %(prog)s feature/local-work --no-push
  
  # Force recreate an existing branch
  %(prog)s feature/restart --force
  
  # Delete a branch
  %(prog)s --delete old-feature
  
  # Delete a branch including remote
  %(prog)s --delete old-feature --delete-remote
        """
    )
    
    parser.add_argument(
        "branch_name",
        nargs="?",
        help="Name of the branch to create/manage"
    )
    
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch to create from (default: main)"
    )
    
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push the branch to remote"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force creation/deletion even if branch exists"
    )
    
    parser.add_argument(
        "--repo-path",
        help="Path to Git repository (default: current directory)"
    )
    
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the specified branch"
    )
    
    parser.add_argument(
        "--delete-remote",
        action="store_true",
        help="Also delete the branch from remote (with --delete)"
    )
    
    parser.add_argument(
        "--switch",
        action="store_true",
        help="Switch to an existing branch instead of creating"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.branch_name:
        parser.error("branch_name is required")
    
    try:
        creator = BranchCreator(repo_path=args.repo_path)
        
        # Handle different operations
        if args.delete:
            success = creator.delete_branch(
                args.branch_name,
                force=args.force,
                delete_remote=args.delete_remote
            )
        elif args.switch:
            success = creator.switch_branch(args.branch_name)
        else:
            success = creator.create_branch(
                args.branch_name,
                base_branch=args.base,
                push=not args.no_push,
                force=args.force
            )
        
        sys.exit(0 if success else 1)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
