"""
Workspace Diff Engine & Incremental Change Detector.

Tracks added, modified, and deleted files using workspace snapshots before and after execution.
"""

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_IGNORE_PATTERNS: set[str] = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".ai",
}


@dataclass(frozen=True)
class FileMetadata:
    """Metadata for a single file in a workspace snapshot."""

    path: str  # POSIX relative path
    size: int
    hash: str  # SHA-256 hex digest
    mtime: float


@dataclass
class WorkspaceSnapshot:
    """Snapshot of files in a workspace at a specific point in time."""

    root_dir: str
    files: dict[str, FileMetadata] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class DiffResult:
    """Result of comparing two workspace snapshots."""

    added_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    unchanged_files: list[str] = field(default_factory=list)

    @property
    def files_changed(self) -> list[str]:
        """Returns deterministic list of all changed files (added + modified + deleted)."""
        combined = set(self.added_files + self.modified_files + self.deleted_files)
        return sorted(combined)



class WorkspaceDiffTracker:
    """Engine for creating and comparing workspace snapshots to track incremental changes."""

    def __init__(
        self,
        workspace_dir: str | Path,
        ignore_patterns: set[str] | list[str] | None = None,
    ) -> None:
        self.workspace_dir = Path(workspace_dir).resolve()
        self.ignore_patterns = (
            set(ignore_patterns)
            if ignore_patterns is not None
            else set(DEFAULT_IGNORE_PATTERNS)
        )

    def _should_ignore(self, rel_path: str, parts: tuple[str, ...]) -> bool:
        """Determines if a relative path or any of its directory parts should be ignored."""
        for part in parts:
            if part in self.ignore_patterns:
                return True
            for pattern in self.ignore_patterns:
                if pattern.startswith("*") and part.endswith(pattern[1:]):
                    return True
        return False

    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """Computes SHA-256 hash of file content in binary mode."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def take_snapshot(self) -> WorkspaceSnapshot:
        """Takes a snapshot of all non-ignored files in the workspace directory."""
        files: dict[str, FileMetadata] = {}
        if not self.workspace_dir.exists() or not self.workspace_dir.is_dir():
            return WorkspaceSnapshot(root_dir=str(self.workspace_dir), files={})

        for root, dirs, filenames in os.walk(self.workspace_dir):
            rel_root = Path(root).relative_to(self.workspace_dir)

            # Exclude ignored directories in-place for performance
            dirs[:] = [
                d
                for d in dirs
                if not self._should_ignore(
                    str(rel_root / d).replace("\\", "/"),
                    (rel_root / d).parts,
                )
            ]

            for filename in filenames:
                file_path = Path(root) / filename
                try:
                    rel_path_obj = file_path.relative_to(self.workspace_dir)
                    rel_path_str = str(rel_path_obj).replace("\\", "/")
                    if self._should_ignore(rel_path_str, rel_path_obj.parts):
                        continue

                    stat = file_path.stat()
                    file_hash = self.compute_file_hash(file_path)
                    files[rel_path_str] = FileMetadata(
                        path=rel_path_str,
                        size=stat.st_size,
                        hash=file_hash,
                        mtime=stat.st_mtime,
                    )
                except (OSError, PermissionError):
                    # Handle unreadable files gracefully
                    continue

        # Sort files dictionary by relative path deterministically
        sorted_files = {k: files[k] for k in sorted(files.keys())}
        return WorkspaceSnapshot(
            root_dir=str(self.workspace_dir),
            files=sorted_files,
        )

    def compare(
        self,
        before: WorkspaceSnapshot,
        after: WorkspaceSnapshot,
    ) -> DiffResult:
        """Compares two snapshots and returns a deterministic DiffResult."""
        before_keys = set(before.files.keys())
        after_keys = set(after.files.keys())

        # Added: files present in after but not in before
        added = sorted(after_keys - before_keys)

        # Deleted: files present in before but not in after
        deleted = sorted(before_keys - after_keys)

        # Common files: check if modified or unchanged
        common_keys = before_keys & after_keys
        modified: list[str] = []
        unchanged: list[str] = []

        for key in sorted(common_keys):

            before_meta = before.files[key]
            after_meta = after.files[key]

            # Compare hash first for exact content comparison
            if (
                before_meta.hash != after_meta.hash
                or before_meta.size != after_meta.size
            ):
                modified.append(key)
            else:
                unchanged.append(key)

        return DiffResult(
            added_files=added,
            modified_files=modified,
            deleted_files=deleted,
            unchanged_files=unchanged,
        )

    def diff_from_snapshot(self, initial_snapshot: WorkspaceSnapshot) -> DiffResult:
        """Convenience method to compare initial snapshot against current workspace state."""
        current_snapshot = self.take_snapshot()
        return self.compare(initial_snapshot, current_snapshot)
