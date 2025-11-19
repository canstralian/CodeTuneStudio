#!/bin/bash
# Setup script for pre-commit hooks
# This script installs and configures pre-commit hooks for local development

set -e

echo "=========================================="
echo "Setting up Pre-commit Hooks"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is not installed"
    echo "Please install pip and try again"
    exit 1
fi

echo "✓ pip found"
echo ""

# Install pre-commit
echo "Installing pre-commit..."
pip install --user pre-commit || pip3 install --user pre-commit

# Verify installation
if ! command -v pre-commit &> /dev/null; then
    echo "⚠ Warning: pre-commit not found in PATH"
    echo "You may need to add ~/.local/bin to your PATH"
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo ""
fi

echo "✓ pre-commit installed"
echo ""

# Install development dependencies
echo "Installing development dependencies (black, flake8)..."
pip install --user black flake8 || pip3 install --user black flake8

echo "✓ Development dependencies installed"
echo ""

# Install pre-commit hooks
if [ -f .pre-commit-config.yaml ]; then
    echo "Installing pre-commit hooks..."
    pre-commit install
    echo "✓ Pre-commit hooks installed"
    echo ""
    
    # Run pre-commit on all files to verify setup
    echo "Running pre-commit on all files (this may take a moment)..."
    if pre-commit run --all-files; then
        echo ""
        echo "✓ All checks passed!"
    else
        echo ""
        echo "⚠ Some checks failed. Please fix the issues and commit again."
        echo "Pre-commit will automatically run on each commit."
    fi
else
    echo "❌ Error: .pre-commit-config.yaml not found"
    echo "Please ensure you're in the project root directory"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Pre-commit hooks will now run automatically before each commit."
echo "To manually run all hooks: pre-commit run --all-files"
echo "To skip hooks for a commit: git commit --no-verify"
echo ""
echo "For more information: https://pre-commit.com"
echo ""
