"""Tests for Context Gate component."""

import pytest
from datetime import datetime
from scripts.ai_review_gate.context import ContextGate
from scripts.ai_review_gate.types import PRChanges, FileChange


@pytest.fixture
def context_gate():
    """Create a ContextGate instance with default settings."""
    return ContextGate(max_files=50, max_lines=5000)


@pytest.fixture
def small_pr():
    """Create a small PR with reasonable changes."""
    files = [
        FileChange(
            filename="app.py",
            status="modified",
            additions=10,
            deletions=5,
            changes=15,
            patch="@@ -1,5 +1,10 @@\n+added line\n-removed line",
        )
    ]

    return PRChanges(
        pr_number=1,
        title="Small change",
        description="Minor update",
        base_ref="main",
        head_ref="feature",
        base_sha="abc123",
        head_sha="def456",
        files=files,
        total_additions=10,
        total_deletions=5,
        total_changes=15,
        file_count=1,
        author="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def large_pr():
    """Create a large PR that exceeds limits."""
    files = [
        FileChange(
            filename=f"file{i}.py",
            status="modified",
            additions=100,
            deletions=50,
            changes=150,
            patch="@@ -1,100 +1,150 @@\n" + "+line\n" * 100,
        )
        for i in range(60)  # Exceeds 50 file limit
    ]

    return PRChanges(
        pr_number=2,
        title="Large refactoring",
        description="Major changes",
        base_ref="main",
        head_ref="refactor",
        base_sha="abc123",
        head_sha="def456",
        files=files,
        total_additions=6000,
        total_deletions=3000,
        total_changes=9000,  # Exceeds 5000 line limit
        file_count=60,
        author="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_small_pr_passes_context_check(context_gate, small_pr):
    """Test that a small PR passes context sufficiency check."""
    result = context_gate.check_context_sufficiency(small_pr)

    assert result.is_sufficient is True
    assert result.reason is None


def test_large_pr_fails_file_count(context_gate, large_pr):
    """Test that PR with too many files fails context check."""
    result = context_gate.check_context_sufficiency(large_pr)

    assert result.is_sufficient is False
    assert "Too many files" in result.reason
    assert result.details["file_count"] == 60


def test_large_pr_fails_line_count(context_gate):
    """Test that PR with too many lines fails context check."""
    files = [
        FileChange(
            filename="app.py",
            status="modified",
            additions=3000,
            deletions=2500,
            changes=5500,
            patch="@@ -1,2500 +1,3000 @@\n" + "+line\n" * 3000,
        )
    ]

    pr = PRChanges(
        pr_number=3,
        title="Large change",
        description="Too many lines",
        base_ref="main",
        head_ref="feature",
        base_sha="abc123",
        head_sha="def456",
        files=files,
        total_additions=3000,
        total_deletions=2500,
        total_changes=5500,  # Exceeds 5000
        file_count=1,
        author="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    result = context_gate.check_context_sufficiency(pr)

    assert result.is_sufficient is False
    assert "Too many lines" in result.reason


def test_binary_files_detected(context_gate):
    """Test that binary files are detected."""
    files = [
        FileChange(
            filename="data.bin",
            status="added",
            additions=0,
            deletions=0,
            changes=0,
            patch=None,
        )
    ]

    pr = PRChanges(
        pr_number=4,
        title="Add binary",
        description="Binary file",
        base_ref="main",
        head_ref="feature",
        base_sha="abc123",
        head_sha="def456",
        files=files,
        total_additions=0,
        total_deletions=0,
        total_changes=0,
        file_count=1,
        author="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    result = context_gate.check_context_sufficiency(pr)

    assert result.is_sufficient is False
    assert "Binary" in result.reason


def test_refusal_message_generation(context_gate):
    """Test that refusal messages are properly formatted."""
    check = context_gate.check_context_sufficiency(
        PRChanges(
            pr_number=5,
            title="Too large",
            description="",
            base_ref="main",
            head_ref="feature",
            base_sha="abc123",
            head_sha="def456",
            files=[],
            total_additions=0,
            total_deletions=0,
            total_changes=10000,  # Way over limit
            file_count=0,
            author="test_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    message = context_gate.generate_refusal_message(check)

    assert "⛔" in message
    assert "INSUFFICIENT CONTEXT" in message
    assert check.reason in message
