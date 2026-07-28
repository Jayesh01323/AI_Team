"""
ArtifactManager — saves/loads all generated artifacts.

Stages no longer write files directly — they delegate here.
"""

import json
from pathlib import Path
from typing import Any

from core.config import PROJECTS_DIR
from core.logging import get_logger

logger = get_logger(__name__)


class ArtifactManager:
    """Manages saving and loading of generated project artifacts."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.project_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def for_project(cls, project_name: str) -> "ArtifactManager":
        """Create an ArtifactManager for a named project."""
        return cls(PROJECTS_DIR / project_name)

    def save_markdown(self, filename: str, content: str) -> Path:
        """Save content as a Markdown file."""
        filepath = self.project_dir / filename
        filepath.write_text(content, encoding="utf-8")
        logger.info("Saved artifact: %s", filepath)
        return filepath

    def save_json(self, filename: str, data: dict[str, Any]) -> Path:
        """Save data as a JSON file."""
        filepath = self.project_dir / filename
        filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("Saved artifact: %s", filepath)
        return filepath

    def load_markdown(self, filename: str) -> str | None:
        """Load a Markdown file, or None if it doesn't exist."""
        filepath = self.project_dir / filename
        return filepath.read_text(encoding="utf-8") if filepath.exists() else None

    def load_json(self, filename: str) -> dict[str, Any] | None:
        """Load a JSON file, or None if it doesn't exist."""
        filepath = self.project_dir / filename
        return (
            json.loads(filepath.read_text(encoding="utf-8"))
            if filepath.exists()
            else None
        )
