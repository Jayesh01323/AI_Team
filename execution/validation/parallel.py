"""
Parallel Validation Engine.

Executes independent validators concurrently using thread pools while preserving
deterministic output ordering and providing fallback to sequential execution.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from core.logging import get_logger
from execution.validation.pipeline import ValidationEngine, ValidationResult, Validator

logger = get_logger(__name__)


class ParallelValidationEngine(ValidationEngine):
    """Validation engine capable of executing independent validators concurrently."""

    def __init__(
        self,
        validators: list[Validator] | None = None,
        max_workers: int = 4,
        parallel: bool = True,
    ) -> None:
        super().__init__(validators=validators)
        self.max_workers = max_workers
        self.parallel = parallel

    def _run_single_validator(
        self,
        validator: Validator,
        workspace_path: Path,
        correlation_id: str | None = None,
    ) -> ValidationResult:
        """Executes a single validator cleanly with exception isolation."""
        try:
            return validator.validate(workspace_path, correlation_id=correlation_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"Validator '{validator.name}' raised an unexpected exception: {e}"
            )
            return ValidationResult(
                success=False,
                validator_name=validator.name,
                errors=[f"Validator failed with internal error: {e}"],
                output="",
                correlation_id=correlation_id,
            )

    def validate(
        self,
        workspace_path: Path,
        correlation_id: str | None = None,
        parallel: bool | None = None,
    ) -> list[ValidationResult]:
        """Executes registered validators concurrently or sequentially.

        Returns results deterministically matching the order of self.validators.
        """
        use_parallel = self.parallel if parallel is None else parallel

        # Fall back to sequential if parallel is disabled or <= 1 validator exists
        if not use_parallel or len(self.validators) <= 1:
            return super().validate(workspace_path, correlation_id=correlation_id)

        workers = min(self.max_workers, len(self.validators))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(
                    self._run_single_validator,
                    validator,
                    workspace_path,
                    correlation_id,
                )
                for validator in self.validators
            ]
            results = [future.result() for future in futures]

        return results
