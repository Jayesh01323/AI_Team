import time
from pathlib import Path

from execution.validation.report import ValidationReport
from execution.validation.validators import (
    is_tool_installed,
    validate_node_project,
    validate_python_project,
    validate_repository_structure,
)


class ValidationRunner:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def run_validation(self) -> ValidationReport:
        start_time = time.time()
        report = ValidationReport()

        report.repository_exists = self.project_dir.exists()
        if not report.repository_exists:
            report.errors.append("Repository directory does not exist")
            report.duration = time.time() - start_time
            return report

        report.git_initialized = (self.project_dir / ".git").exists()

        # Tools
        if not is_tool_installed("python"):
            report.warnings.append("Python is not installed or not in PATH")
        if not is_tool_installed("npm"):
            report.warnings.append("npm is not installed or not in PATH")
        if not is_tool_installed("git"):
            report.warnings.append("Git is not installed or not in PATH")
        if not is_tool_installed("docker"):
            report.warnings.append("Docker is not installed or not in PATH")

        # Structure
        struct_errors, struct_warnings = validate_repository_structure(self.project_dir)
        report.errors.extend(struct_errors)
        report.warnings.extend(struct_warnings)

        # Python
        if (self.project_dir / "backend").exists() or (
            self.project_dir / "pyproject.toml"
        ).exists():
            py_errors = validate_python_project(self.project_dir)
            if py_errors:
                report.errors.extend(py_errors)
            else:
                report.python_validation = True

        # Node
        if (self.project_dir / "frontend").exists():
            node_errors = validate_node_project(self.project_dir)
            if node_errors:
                report.errors.extend(node_errors)
            else:
                report.node_validation = True

        report.duration = time.time() - start_time
        return report
