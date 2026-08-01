import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationResult:
    success: bool
    validator_name: str
    errors: list[str] = field(default_factory=list)
    output: str = ""
    correlation_id: str | None = None


class Validator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def validate(
        self, workspace_path: Path, correlation_id: str | None = None
    ) -> ValidationResult:
        pass


class RuffValidator(Validator):
    @property
    def name(self) -> str:
        return "RuffLinter"

    def validate(
        self, workspace_path: Path, correlation_id: str | None = None
    ) -> ValidationResult:
        try:
            res = subprocess.run(
                ["ruff", "check", "."],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            success = res.returncode == 0
            errors = [] if success else [res.stdout + res.stderr]
            return ValidationResult(
                success=success,
                validator_name=self.name,
                errors=errors,
                output=res.stdout + res.stderr,
                correlation_id=correlation_id,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                success=False,
                validator_name=self.name,
                errors=["Validation timed out after 60 seconds"],
                output="",
                correlation_id=correlation_id,
            )
        except Exception as e:  # noqa: BLE001
            return ValidationResult(
                success=False,
                validator_name=self.name,
                errors=[f"Failed to execute ruff check: {e}"],
                output="",
                correlation_id=correlation_id,
            )


class RuffFormatValidator(Validator):
    @property
    def name(self) -> str:
        return "RuffFormatter"

    def validate(
        self, workspace_path: Path, correlation_id: str | None = None
    ) -> ValidationResult:
        try:
            res = subprocess.run(
                ["ruff", "format", "--check", "."],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            success = res.returncode == 0
            errors = [] if success else [res.stdout + res.stderr]
            return ValidationResult(
                success=success,
                validator_name=self.name,
                errors=errors,
                output=res.stdout + res.stderr,
                correlation_id=correlation_id,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                success=False,
                validator_name=self.name,
                errors=["Validation timed out after 60 seconds"],
                output="",
                correlation_id=correlation_id,
            )
        except Exception as e:  # noqa: BLE001
            return ValidationResult(
                success=False,
                validator_name=self.name,
                errors=[f"Failed to execute ruff format check: {e}"],
                output="",
                correlation_id=correlation_id,
            )


class PytestValidator(Validator):
    @property
    def name(self) -> str:
        return "Pytest"

    def validate(
        self, workspace_path: Path, correlation_id: str | None = None
    ) -> ValidationResult:
        try:
            res = subprocess.run(
                ["pytest", "."],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            success = res.returncode == 0
            errors = [] if success else [res.stdout + res.stderr]
            return ValidationResult(
                success=success,
                validator_name=self.name,
                errors=errors,
                output=res.stdout + res.stderr,
                correlation_id=correlation_id,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                success=False,
                validator_name=self.name,
                errors=["Validation timed out after 60 seconds"],
                output="",
                correlation_id=correlation_id,
            )
        except Exception as e:  # noqa: BLE001
            return ValidationResult(
                success=False,
                validator_name=self.name,
                errors=[f"Failed to execute pytest: {e}"],
                output="",
                correlation_id=correlation_id,
            )


class ValidationEngine:
    def __init__(self, validators: list[Validator] | None = None):
        self.validators = (
            validators
            if validators is not None
            else [
                RuffValidator(),
                RuffFormatValidator(),
                PytestValidator(),
            ]
        )

    def validate(
        self, workspace_path: Path, correlation_id: str | None = None
    ) -> list[ValidationResult]:
        results = []
        for validator in self.validators:
            try:
                res = validator.validate(workspace_path, correlation_id=correlation_id)
                results.append(res)
            except Exception as e:  # noqa: BLE001
                results.append(
                    ValidationResult(
                        success=False,
                        validator_name=validator.name,
                        errors=[f"Validator failed with internal error: {e}"],
                        output="",
                        correlation_id=correlation_id,
                    )
                )
        return results
