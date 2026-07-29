import json
import subprocess
from pathlib import Path


def is_tool_installed(tool_name: str) -> bool:
    try:
        subprocess.run(
            [tool_name, "--version"], capture_output=True, check=True, timeout=5
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        OSError,
        subprocess.TimeoutExpired,
    ):
        return False


def validate_repository_structure(project_dir: Path) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings)"""
    errors = []

    # Check basic files
    for f in [
        "README.md",
        ".gitignore",
        "pyproject.toml",
        "docker-compose.yml",
        ".env.example",
    ]:
        if not (project_dir / f).exists():
            errors.append(f"Missing required file: {f}")

    # Check basic dirs
    for d in ["backend", "frontend", "docs", "tests", ".git"]:
        if not (project_dir / d).exists():
            errors.append(f"Missing required directory: {d}")

    return errors, []


def validate_python_project(project_dir: Path) -> list[str]:
    errors = []
    pyproject = project_dir / "pyproject.toml"
    reqs = project_dir / "backend" / "requirements.txt"

    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "[project]" not in content:
                errors.append("Invalid pyproject.toml: missing [project] section")
        except OSError as e:
            errors.append(f"Error reading pyproject.toml: {e}")

    if reqs.exists():
        content = reqs.read_text(encoding="utf-8")
        if not content.strip():
            errors.append("requirements.txt is empty")

    return errors


def validate_node_project(project_dir: Path) -> list[str]:
    errors = []
    pkg = project_dir / "frontend" / "package.json"
    if pkg.exists():
        try:
            with open(pkg, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "name" not in data or "version" not in data:
                    errors.append("Invalid package.json: missing name or version")
        except json.JSONDecodeError:
            errors.append("Invalid JSON in package.json")
    return errors
