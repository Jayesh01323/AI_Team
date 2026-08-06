"""
Self-Healing Error Recovery Engine.

Detects execution/validation failures, classifies error types, enforces retry budgets,
and generates structured recovery decisions and remediation prompts.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.exceptions import (
    ConfigurationError,
    ProjectExistsError,
    ProviderAuthenticationError,
    ProviderCapabilityError,
    ProviderConfigurationError,
    ProviderNotImplementedError,
    ProviderNotRegisteredError,
)
from execution.recovery.prompts import format_recovery_prompt
from execution.validation.pipeline import ValidationResult
from models.execution import ExecutionResult


class FailureCategory(str, Enum):
    """Categorization of execution and validation failures."""

    NONE = "NONE"
    RECOVERABLE_VALIDATION = "RECOVERABLE_VALIDATION"
    RECOVERABLE_EXECUTION = "RECOVERABLE_EXECUTION"
    NON_RECOVERABLE = "NON_RECOVERABLE"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"


NON_RECOVERABLE_EXCEPTIONS: tuple[type[Exception], ...] = (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderNotRegisteredError,
    ProviderNotImplementedError,
    ProviderCapabilityError,
    ConfigurationError,
    ProjectExistsError,
    ValueError,
    FileNotFoundError,
)


@dataclass
class RecoveryAttempt:
    """Audit trail record for a single recovery attempt."""

    attempt: int
    category: FailureCategory
    reason: str
    errors: list[str] = field(default_factory=list)
    remediation_prompt: str | None = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class RecoveryDecision:
    """Structured decision returned by SelfHealingEngine."""

    should_retry: bool
    category: FailureCategory
    reason: str
    attempt: int
    max_retries: int
    remediation_prompt: str | None = None
    history: list[RecoveryAttempt] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Exposes structured metadata for execution reporting."""
        return {
            "should_retry": self.should_retry,
            "category": self.category.value,
            "reason": self.reason,
            "attempt": self.attempt,
            "max_retries": self.max_retries,
            "has_remediation_prompt": self.remediation_prompt is not None,
            "history_count": len(self.history),
        }


class SelfHealingEngine:
    """Engine for classifying failures and evaluating self-healing retry strategies."""

    def __init__(
        self,
        max_retries: int = 3,
        non_recoverable_types: tuple[type[Exception], ...] | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.non_recoverable_types = (
            non_recoverable_types
            if non_recoverable_types is not None
            else NON_RECOVERABLE_EXCEPTIONS
        )

    def classify_failure(
        self,
        adapter_result: ExecutionResult | None,
        validation_results: list[ValidationResult],
        exception: Exception | None = None,
    ) -> tuple[FailureCategory, str, list[str]]:
        """Classifies a failure state into a FailureCategory with explanation and error messages."""
        # 1. Exception-based check
        if exception is not None:
            if isinstance(exception, self.non_recoverable_types):
                return (
                    FailureCategory.NON_RECOVERABLE,
                    f"Non-recoverable exception: {type(exception).__name__} ({exception})",
                    [str(exception)],
                )
            return (
                FailureCategory.RECOVERABLE_EXECUTION,
                f"Execution exception: {type(exception).__name__} ({exception})",
                [str(exception)],
            )

        # 2. Adapter execution status check
        if adapter_result is not None and (
            adapter_result.exit_code != 0 or adapter_result.status == "FAILED"
        ):
            error_msg = adapter_result.error_log or "Adapter execution returned non-zero exit code"
            return (
                FailureCategory.RECOVERABLE_EXECUTION,
                f"Adapter execution failed: {error_msg}",
                adapter_result.errors or [error_msg],
            )

        # 3. Validation results check
        failing_validators = [r for r in validation_results if not r.success]
        if failing_validators:
            all_errors: list[str] = []
            names = []
            for val in failing_validators:
                names.append(val.validator_name)
                all_errors.extend(val.errors)

            reason = f"Validation failed for: {', '.join(names)}"
            return (
                FailureCategory.RECOVERABLE_VALIDATION,
                reason,
                all_errors,
            )

        return (
            FailureCategory.NONE,
            "Execution and validation succeeded.",
            [],
        )

    def evaluate_recovery(
        self,
        original_instruction: str,
        adapter_result: ExecutionResult | None,
        validation_results: list[ValidationResult],
        current_attempt: int,
        exception: Exception | None = None,
        history: list[RecoveryAttempt] | None = None,
    ) -> RecoveryDecision:
        """Evaluates whether to retry an execution turn given current attempt and validation feedback."""
        current_history = list(history) if history is not None else []
        category, reason, errors = self.classify_failure(
            adapter_result, validation_results, exception
        )

        # Success case
        if category == FailureCategory.NONE:
            return RecoveryDecision(
                should_retry=False,
                category=FailureCategory.NONE,
                reason=reason,
                attempt=current_attempt,
                max_retries=self.max_retries,
                history=current_history,
            )

        # Non-recoverable failure
        if category == FailureCategory.NON_RECOVERABLE:
            attempt_record = RecoveryAttempt(
                attempt=current_attempt,
                category=category,
                reason=reason,
                errors=errors,
                remediation_prompt=None,
            )
            current_history.append(attempt_record)
            return RecoveryDecision(
                should_retry=False,
                category=FailureCategory.NON_RECOVERABLE,
                reason=reason,
                attempt=current_attempt,
                max_retries=self.max_retries,
                history=current_history,
            )

        # Retry limit exhausted
        if current_attempt >= self.max_retries:
            exhausted_reason = (
                f"Retry limit exhausted ({current_attempt}/{self.max_retries}). {reason}"
            )
            attempt_record = RecoveryAttempt(
                attempt=current_attempt,
                category=FailureCategory.RETRY_EXHAUSTED,
                reason=exhausted_reason,
                errors=errors,
                remediation_prompt=None,
            )
            current_history.append(attempt_record)
            return RecoveryDecision(
                should_retry=False,
                category=FailureCategory.RETRY_EXHAUSTED,
                reason=exhausted_reason,
                attempt=current_attempt,
                max_retries=self.max_retries,
                history=current_history,
            )

        # Recoverable case (validation or execution failure within budget)
        next_attempt = current_attempt + 1
        error_log = adapter_result.error_log if adapter_result else (str(exception) if exception else None)
        remediation_prompt = format_recovery_prompt(
            original_instruction=original_instruction,
            validation_results=validation_results,
            attempt=next_attempt,
            max_retries=self.max_retries,
            error_log=error_log,
        )

        attempt_record = RecoveryAttempt(
            attempt=current_attempt,
            category=category,
            reason=reason,
            errors=errors,
            remediation_prompt=remediation_prompt,
        )
        current_history.append(attempt_record)

        return RecoveryDecision(
            should_retry=True,
            category=category,
            reason=reason,
            attempt=next_attempt,
            max_retries=self.max_retries,
            remediation_prompt=remediation_prompt,
            history=current_history,
        )
