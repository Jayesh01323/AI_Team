from dataclasses import dataclass, field


@dataclass
class ValidationReport:
    repository_exists: bool = False
    git_initialized: bool = False
    required_files: list[str] = field(default_factory=list)
    required_directories: list[str] = field(default_factory=list)
    python_validation: bool = False
    node_validation: bool = False
    docker_validation: bool = False
    lint_status: bool = False
    test_status: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0

    def is_successful(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "repository_exists": self.repository_exists,
            "git_initialized": self.git_initialized,
            "required_files": self.required_files,
            "required_directories": self.required_directories,
            "python_validation": self.python_validation,
            "node_validation": self.node_validation,
            "docker_validation": self.docker_validation,
            "lint_status": self.lint_status,
            "test_status": self.test_status,
            "warnings": self.warnings,
            "errors": self.errors,
            "duration": self.duration,
        }
