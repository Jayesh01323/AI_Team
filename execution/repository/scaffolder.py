import subprocess

from execution.repository.filesystem import FileSystem
from models.project_context import ProjectContext


class ProjectScaffolder:
    """Scaffolds standard directories and boilerplate files."""

    def __init__(self, fs: FileSystem):
        self.fs = fs

    def create_root(self) -> None:
        self.fs.create_directory("")

    def create_standard_directories(self, context: ProjectContext) -> None:
        dirs = [
            "backend",
            "frontend",
            "shared",
            "docs",
            "tests",
            "scripts",
            ".github/workflows",
        ]
        for d in dirs:
            self.fs.create_directory(d)

    def initialize_git(self) -> None:
        try:
            subprocess.run(
                ["git", "init"],
                cwd=str(self.fs.root_dir),
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to initialize git: {e.stderr.decode()}") from e

    def scaffold(self, context: ProjectContext) -> list[str]:
        """Runs base scaffolding steps and returns created files."""
        self.create_root()
        self.create_standard_directories(context)
        self.initialize_git()
        return self.fs.list_files()
