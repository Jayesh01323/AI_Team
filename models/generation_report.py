from dataclasses import dataclass, field
from datetime import datetime

from execution.validation.report import ValidationReport


@dataclass
class ValidationStep:
    """Represents a single validation step (e.g. Build, Test, Lint)."""

    step_name: str
    status: str  # e.g., 'SUCCESS', 'FAILED', 'PENDING'
    logs: str
    exit_code: int


@dataclass
class GenerationReport:
    """Design contract for the Generation Report output by the Repository Generator."""

    project_name: str
    repository_path: str
    created_at: datetime
    status: str  # e.g., 'SUCCESS', 'FAILED'

    files_created: list[str] = field(default_factory=list)
    validation_steps: list[ValidationStep] = field(default_factory=list)
    validation_report: ValidationReport | None = None

    error_message: str | None = None

    def is_successful(self) -> bool:
        """Returns True if generation and all validation steps succeeded."""
        if self.status != "SUCCESS":
            return False
        return all(step.status == "SUCCESS" for step in self.validation_steps)

    def to_dict(self) -> dict:
        """Serializes the report to a dictionary."""
        return {
            "project_name": self.project_name,
            "repository_path": self.repository_path,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "files_created": self.files_created,
            "validation_steps": [
                {
                    "step_name": step.step_name,
                    "status": step.status,
                    "logs": step.logs,
                    "exit_code": step.exit_code,
                }
                for step in self.validation_steps
            ],
            "validation_report": self.validation_report.to_dict()
            if self.validation_report
            else None,
            "error_message": self.error_message,
        }
