"""
Unit tests for WorkspaceDiffTracker & Incremental Change Detector (M6-TASK-001).
"""

from pathlib import Path

import pytest

from execution.diff_tracker import (
    WorkspaceDiffTracker,
    WorkspaceSnapshot,
)


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Fixture providing a clean temporary workspace directory."""
    ws = tmp_path / "test_ws"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def test_empty_workspace_snapshot(temp_workspace: Path) -> None:
    """Test snapshot of an empty workspace."""
    tracker = WorkspaceDiffTracker(temp_workspace)
    snapshot = tracker.take_snapshot()

    assert isinstance(snapshot, WorkspaceSnapshot)
    assert len(snapshot.files) == 0


def test_added_files_detection(temp_workspace: Path) -> None:
    """Test detection of added files between snapshots."""
    tracker = WorkspaceDiffTracker(temp_workspace)
    before = tracker.take_snapshot()

    # Add files
    file1 = temp_workspace / "hello.txt"
    file1.write_text("Hello World", encoding="utf-8")
    file2 = temp_workspace / "src" / "main.py"
    file2.parent.mkdir(parents=True, exist_ok=True)
    file2.write_text("print('hello')", encoding="utf-8")

    after = tracker.take_snapshot()
    diff = tracker.compare(before, after)

    assert diff.added_files == ["hello.txt", "src/main.py"]
    assert diff.modified_files == []
    assert diff.deleted_files == []
    assert diff.unchanged_files == []
    assert diff.files_changed == ["hello.txt", "src/main.py"]


def test_modified_files_detection(temp_workspace: Path) -> None:
    """Test detection of modified files between snapshots."""
    tracker = WorkspaceDiffTracker(temp_workspace)

    # Initial file setup
    file1 = temp_workspace / "config.json"
    file1.write_text('{"version": 1}', encoding="utf-8")
    before = tracker.take_snapshot()

    # Modify file
    file1.write_text('{"version": 2}', encoding="utf-8")
    after = tracker.take_snapshot()
    diff = tracker.compare(before, after)

    assert diff.added_files == []
    assert diff.modified_files == ["config.json"]
    assert diff.deleted_files == []
    assert diff.unchanged_files == []
    assert diff.files_changed == ["config.json"]


def test_deleted_files_detection(temp_workspace: Path) -> None:
    """Test detection of deleted files between snapshots."""
    tracker = WorkspaceDiffTracker(temp_workspace)

    # Setup files
    file1 = temp_workspace / "temp.log"
    file1.write_text("logging data", encoding="utf-8")
    file2 = temp_workspace / "keep.txt"
    file2.write_text("keep me", encoding="utf-8")
    before = tracker.take_snapshot()

    # Delete temp.log
    file1.unlink()
    after = tracker.take_snapshot()
    diff = tracker.compare(before, after)

    assert diff.added_files == []
    assert diff.modified_files == []
    assert diff.deleted_files == ["temp.log"]
    assert diff.unchanged_files == ["keep.txt"]
    assert diff.files_changed == ["temp.log"]


def test_unchanged_files(temp_workspace: Path) -> None:
    """Test that unchanged files are properly categorized and excluded from files_changed."""
    tracker = WorkspaceDiffTracker(temp_workspace)

    file1 = temp_workspace / "static.txt"
    file1.write_text("static content", encoding="utf-8")
    before = tracker.take_snapshot()

    # Re-take snapshot without modifying
    after = tracker.take_snapshot()
    diff = tracker.compare(before, after)

    assert diff.added_files == []
    assert diff.modified_files == []
    assert diff.deleted_files == []
    assert diff.unchanged_files == ["static.txt"]
    assert diff.files_changed == []


def test_nested_directories_and_deterministic_ordering(temp_workspace: Path) -> None:
    """Test deep nested directory handling and deterministic alphabetical sorting."""
    tracker = WorkspaceDiffTracker(temp_workspace)

    # Create files in non-alphabetical order
    (temp_workspace / "z_file.py").write_text("z", encoding="utf-8")
    (temp_workspace / "a_file.py").write_text("a", encoding="utf-8")
    (temp_workspace / "b").mkdir(parents=True, exist_ok=True)
    (temp_workspace / "b" / "sub_b.py").write_text("sub_b", encoding="utf-8")
    (temp_workspace / "b" / "sub_a.py").write_text("sub_a", encoding="utf-8")


    before = tracker.take_snapshot()
    assert list(before.files.keys()) == [
        "a_file.py",
        "b/sub_a.py",
        "b/sub_b.py",
        "z_file.py",
    ]


def test_binary_files_handling(temp_workspace: Path) -> None:
    """Test that binary files are snapshotted and compared correctly via SHA-256."""
    tracker = WorkspaceDiffTracker(temp_workspace)

    binary_file = temp_workspace / "data.bin"
    binary_content_v1 = bytes([0x00, 0xFF, 0xFE, 0xFA, 0x12, 0x34])
    binary_file.write_bytes(binary_content_v1)

    before = tracker.take_snapshot()
    assert "data.bin" in before.files
    assert isinstance(before.files["data.bin"].hash, str)

    # Modify binary content
    binary_content_v2 = bytes([0x00, 0xFF, 0xFE, 0xFA, 0x12, 0x35])
    binary_file.write_bytes(binary_content_v2)

    after = tracker.take_snapshot()
    diff = tracker.compare(before, after)

    assert diff.modified_files == ["data.bin"]


def test_ignore_patterns(temp_workspace: Path) -> None:
    """Test ignoring .git, __pycache__, .ai, and custom patterns."""
    tracker = WorkspaceDiffTracker(temp_workspace)

    # Create normal file
    (temp_workspace / "main.py").write_text("print(1)", encoding="utf-8")

    # Create ignored directories and files
    git_dir = temp_workspace / ".git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    pycache_dir = temp_workspace / "__pycache__"
    pycache_dir.mkdir(parents=True, exist_ok=True)
    (pycache_dir / "main.cpython-311.pyc").write_bytes(b"pyc content")

    ai_dir = temp_workspace / ".ai"
    ai_dir.mkdir(parents=True, exist_ok=True)
    (ai_dir / "contract.json").write_text("{}", encoding="utf-8")

    snapshot = tracker.take_snapshot()

    assert "main.py" in snapshot.files
    assert ".git/HEAD" not in snapshot.files
    assert "__pycache__/main.cpython-311.pyc" not in snapshot.files
    assert ".ai/contract.json" not in snapshot.files


def test_diff_from_snapshot_convenience_method(temp_workspace: Path) -> None:
    """Test the diff_from_snapshot convenience method."""
    tracker = WorkspaceDiffTracker(temp_workspace)
    (temp_workspace / "initial.txt").write_text("initial", encoding="utf-8")

    before = tracker.take_snapshot()

    # Create a new file after taking snapshot
    (temp_workspace / "added.txt").write_text("added", encoding="utf-8")

    diff = tracker.diff_from_snapshot(before)
    assert diff.added_files == ["added.txt"]
