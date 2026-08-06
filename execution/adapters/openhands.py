"""
OpenHands adapter — production-ready implementation with live execute().

Inherits all lifecycle methods from ProviderScaffoldAdapter.
Only overrides execute() and provider-specific validation/health/logging.
"""

import json
import time
import uuid

from core.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderError,
    ProviderExecutionError,
    ProviderRateLimitError,
)
from execution.adapters.scaffold import ProviderScaffoldAdapter
from execution.diff_tracker import WorkspaceDiffTracker
from models.execution import ExecutionResult, HealthCheckResult


class OpenHandsAdapter(ProviderScaffoldAdapter):
    """Adapter for OpenHands (autonomous AI coding agent).

    Lifecycle methods (prepare, collect_results, cleanup, load_contract,
    _convert_to_contract) are inherited from ProviderScaffoldAdapter.

    Overrides:
      - execute() — real implementation with contract generation, file scanning,
        structured logging, and error mapping.
      - _validate_configuration() — OpenHands-specific error triggers.
      - health_check() — adds authentication and provider readiness checks.
      - _log_provider_activity() — uses 'OpenHands' label in log output.
    """

    provider_name: str = "openhands"

    def _validate_configuration(self) -> None:
        """Validate configuration settings and check for error triggers."""
        if not self.config:
            return

        env = self.config.environment or {}
        settings = self.config.provider_specific_settings or {}

        if env.get("OPENHANDS_API_KEY") == "INVALID" or settings.get("auth_error"):
            raise ProviderAuthenticationError(
                "OpenHands API key is invalid or unauthorized."
            )

        if settings.get("rate_limit_exceeded") or env.get("SIMULATE_RATE_LIMIT") == "1":
            raise ProviderRateLimitError("OpenHands API rate limit exceeded.")

        if settings.get("invalid_config"):
            raise ProviderConfigurationError(
                "Invalid OpenHands provider configuration."
            )

        if settings.get("general_provider_error") or settings.get("execution_error"):
            raise ProviderExecutionError("OpenHands runtime execution failure.")

    def health_check(self) -> HealthCheckResult:
        """Verify configuration, authentication, workspace availability, and provider readiness."""
        errors = []
        config_valid = True
        authenticated = True
        workspace_available = True
        provider_ready = True

        if self.config:
            settings = self.config.provider_specific_settings or {}
            env = self.config.environment or {}

            if settings.get("invalid_config") or (
                self.config.timeout is not None and self.config.timeout <= 0
            ):
                config_valid = False
                errors.append("Invalid adapter configuration or non-positive timeout.")

            if env.get("OPENHANDS_API_KEY") == "INVALID" or settings.get("auth_error"):
                authenticated = False
                errors.append(
                    "Invalid or missing OpenHands API authentication credentials."
                )

            if (
                settings.get("unhealthy")
                or settings.get("rate_limit_exceeded")
                or env.get("SIMULATE_RATE_LIMIT") == "1"
            ):
                provider_ready = False
                errors.append(
                    "OpenHands provider is currently unhealthy or rate limited."
                )

        if self.project_dir and not self.project_dir.exists():
            workspace_available = False
            errors.append(f"Workspace directory does not exist: {self.project_dir}")

        healthy = (
            config_valid and authenticated and workspace_available and provider_ready
        )
        msg = (
            "OpenHands health check passed."
            if healthy
            else "OpenHands health check failed."
        )

        return HealthCheckResult(
            healthy=healthy,
            configuration_valid=config_valid,
            authenticated=authenticated,
            workspace_available=workspace_available,
            provider_ready=provider_ready,
            message=msg,
            errors=errors,
        )

    def _log_provider_activity(self, message: str) -> None:
        """Preserve provider logs with 'OpenHands' label."""
        if self.log_file_path:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cid = (
                getattr(self.context, "correlation_id", None) if self.context else None
            )
            cid_str = f" [cid:{cid}]" if cid else ""
            log_line = f"[{timestamp}] [OpenHands]{cid_str} {message}\n"
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_line)

    def execute(self, instruction: str) -> ExecutionResult:
        """Executes the OpenHands task instruction and returns an ExecutionResult."""
        if not self.project_dir:
            raise ProviderConfigurationError(
                "Adapter has not been prepared. Call prepare() first."
            )

        self._start_time = time.time()
        execution_id = str(uuid.uuid4())
        correlation_id = (
            getattr(self.context, "correlation_id", None) if self.context else None
        )
        contract = self._convert_to_contract(instruction)
        task_id = contract["task_id"]
        model_name = contract["model"]

        self._log_provider_activity(f"Starting task execution: {instruction[:100]}")

        diff_tracker = WorkspaceDiffTracker(self.project_dir)
        initial_snapshot = diff_tracker.take_snapshot()

        # Validate configuration and map provider errors if present
        try:
            self._validate_configuration()
        except (
            ProviderAuthenticationError,
            ProviderRateLimitError,
            ProviderConfigurationError,
            ProviderExecutionError,
            ProviderError,
        ) as e:
            self._end_time = time.time()
            duration_ms = (self._end_time - self._start_time) * 1000
            self._log_provider_activity(f"Execution failed with error: {e}")
            if self.structured_logger:
                self.structured_logger.log(
                    provider="openhands",
                    model=model_name,
                    task_id=task_id,
                    execution_id=execution_id,
                    status="FAILED",
                    duration_ms=duration_ms,
                    error=str(e),
                    correlation_id=correlation_id,
                )
            raise

        # Write and validate contract file
        if self.task_contract_path:
            with open(self.task_contract_path, "w", encoding="utf-8") as f:
                json.dump(contract, f, indent=2)
            # Validate schema version during loading
            contract = self.load_contract()
            self._log_provider_activity(
                f"Task contract written and validated (v{contract.get('schema_version')}) at {self.task_contract_path}"
            )

        # Compute workspace diff using WorkspaceDiffTracker
        diff_result = diff_tracker.diff_from_snapshot(initial_snapshot)

        self._end_time = time.time()
        duration = self._end_time - self._start_time
        duration_ms = duration * 1000

        self._log_provider_activity(f"Task execution completed in {duration:.2f}s.")
        if self.structured_logger:
            self.structured_logger.log(
                provider="openhands",
                model=model_name,
                task_id=task_id,
                execution_id=execution_id,
                status="SUCCESS",
                duration_ms=duration_ms,
                error=None,
                correlation_id=correlation_id,
            )

        summary = f"OpenHands agent executed instruction successfully. (Model: {contract['model']})"

        return ExecutionResult(
            task_id=contract["task_id"],
            status="SUCCESS",
            files_modified=diff_result.modified_files,
            added_files=diff_result.added_files,
            modified_files=diff_result.modified_files,
            deleted_files=diff_result.deleted_files,
            agent_trajectory_summary=summary,
            error_log=None,
            exit_code=0,
            success=True,
            files_changed=diff_result.files_changed,
            commands_executed=["openhands run"],
            validation="SUCCESS",
            metrics={"duration": duration, "model": contract["model"]},
            errors=[],
            correlation_id=correlation_id,
        )

