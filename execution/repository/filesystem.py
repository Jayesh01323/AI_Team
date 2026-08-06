import os
from pathlib import Path


class FileSystem:
    """Abstraction for safe file system operations within a repository root."""

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir).resolve()

    def _validate_path(self, path: str | Path) -> Path:
        """Ensures the path is within the root_dir to prevent directory traversal attacks."""
        target_path = (self.root_dir / path).resolve()
        if not target_path.is_relative_to(self.root_dir):
            raise ValueError(
                f"Path {path} is outside the repository root {self.root_dir}"
            )
        return target_path

    def create_directory(self, path: str | Path) -> Path:
        """Creates a directory safely."""
        target_path = self._validate_path(path)
        target_path.mkdir(parents=True, exist_ok=True)
        return target_path

    def write_file(
        self, path: str | Path, content: str, overwrite: bool = False
    ) -> Path:
        """Writes content to a file safely."""
        target_path = self._validate_path(path)
        if target_path.exists() and not overwrite:
            raise FileExistsError(f"File {path} already exists.")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        return target_path

    def file_exists(self, path: str | Path) -> bool:
        """Checks if a file exists."""
        return self._validate_path(path).is_file()

    def dir_exists(self, path: str | Path) -> bool:
        """Checks if a directory exists."""
        return self._validate_path(path).is_dir()

    def list_files(self) -> list[str]:
        """Returns a list of all files relative to root_dir."""
        files = []
        for root, _, filenames in os.walk(self.root_dir):
            # Skip git internals — check for exact ".git" path component
            # to avoid false positives on ".github" etc.
            root_path = Path(root)
            if ".git" in root_path.relative_to(self.root_dir).parts:
                continue
            for filename in filenames:
                full_path = root_path / filename
                files.append(
                    str(full_path.relative_to(self.root_dir)).replace("\\", "/")
                )
        return sorted(files)
