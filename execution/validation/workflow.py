from pathlib import Path

from execution.validation.report import ValidationReport
from execution.validation.runner import ValidationRunner


class ValidationWorkflow:
    @staticmethod
    def run(project_dir: Path) -> ValidationReport:
        runner = ValidationRunner(project_dir)
        return runner.run_validation()
