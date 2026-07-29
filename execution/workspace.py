import shutil
import uuid
from pathlib import Path

from core.config import PROJECTS_DIR
from core.logging import get_logger

logger = get_logger(__name__)


class WorkspaceManager:
    def __init__(self, base_workspaces_dir: Path | None = None):
        if base_workspaces_dir is None:
            self.base_workspaces_dir = PROJECTS_DIR / ".workspaces"
        else:
            self.base_workspaces_dir = Path(base_workspaces_dir)
        self.base_workspaces_dir.mkdir(parents=True, exist_ok=True)

    def verify_repository_exists(self, repo_path: str | Path) -> bool:
        """Verifies if the source repository exists on disk."""
        path = Path(repo_path)
        if not path.is_absolute():
            path = PROJECTS_DIR / path
        return path.exists() and path.is_dir()

    def create_workspace(self, repo_path: str | Path) -> Path:
        """Creates an isolated workspace directory by copying the repository."""
        if not self.verify_repository_exists(repo_path):
            raise FileNotFoundError(f"Source repository does not exist: {repo_path}")

        src_path = Path(repo_path)
        if not src_path.is_absolute():
            src_path = PROJECTS_DIR / src_path

        workspace_id = str(uuid.uuid4())
        dest_path = self.base_workspaces_dir / workspace_id
        dest_path.mkdir(parents=True, exist_ok=True)

        # Copy repository contents, skipping the workspaces dir if nested
        for item in src_path.iterdir():
            if item.name == ".workspaces" or item.name == "projects":
                continue
            if item.is_dir():
                shutil.copytree(item, dest_path / item.name, symlinks=True)
            else:
                shutil.copy2(item, dest_path / item.name)

        logger.info(f"Created workspace at: {dest_path}")
        return dest_path

    def cleanup(self, workspace_path: str | Path) -> None:
        """Cleans up the workspace directory."""
        path = Path(workspace_path)
        # Verify the path is within our workspaces dir for safety
        if path.exists() and path.is_relative_to(self.base_workspaces_dir):
            shutil.rmtree(path)
            logger.info(f"Cleaned up workspace at: {path}")
        else:
            logger.warning(f"Skipping workspace cleanup for path outside base: {path}")
