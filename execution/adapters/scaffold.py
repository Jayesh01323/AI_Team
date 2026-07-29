"""
Base scaffold adapter mixin for providers without a live API integration.

Provides working implementations for:
  - prepare()
  - collect_results()
  - cleanup()
  - health_check()
  - contract generation
  - structured JSON logging
  - correlation_id propagation
  - schema version validation
  - standardized exception mapping

Subclasses override only execute() to raise ProviderNotImplementedError.
"""

import time
import uuid
from pathlib import Path
from typing import Any

from core.exceptions import (
    ProviderConfigurationError,
)
from execution.adapters.base import ExecutionAdapter
from execution.adapters.contract import load_and_validate_contract
from execution.adapters.logger import ProviderStructuredLogger
from models.execution import AdapterConfiguration, ExecutionResult, HealthCheckResult
from models.project_context import ProjectContext


class ProviderScaffoldAdapter(ExecutionAdapter):
    """Mixin-style base for scaffold adapters that lack a live API.

    Concrete subclasses provide:
      - provider_name (class constant)
      - _convert_to_contract (override for provider-specific contract fields)
    """

    provider_name: str = "scaffold"

    def __init__(self, config: AdapterConfiguration | None = None):
        self.config: AdapterConfiguration | None = config
        self.context: ProjectContext | None = None
        self.project_dir: Path | None = None
        self.task_contract_path: Path | None = None
        self.log_file_path: Path | None = None
        self.json_log_path: Path | None = None
        self.structured_logger: ProviderStructuredLogger | None = None
        self._start_time: float | None = None
        self._end_time: float | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def prepare(self, context: ProjectContext, project_dir: Path) -> None:
        """Prepare the workspace environment and setup contract/log paths."""
        if project_dir is None:
            raise ProviderConfigurationError("Workspace project_dir cannot be None.")

        self.project_dir = Path(project_dir)
        if not self.project_dir.exists():
            raise ProviderConfigurationError(
                f"Target workspace directory does not exist: {self.project_dir}"
            )

        self.context = context
        ai_dir = self.project_dir / ".ai"
        ai_dir.mkdir(parents=True, exist_ok=True)

        logs_dir = ai_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        self.task_contract_path = ai_dir / f"{self.provider_name}_contract.json"
        self.log_file_path = logs_dir / f"{self.provider_name}.log"
        self.json_log_path = logs_dir / f"{self.provider_name}.jsonl"
        self.structured_logger = ProviderStructuredLogger(self.json_log_path)

    def health_check(self) -> HealthCheckResult:
        """Verify configuration and workspace availability."""
        errors = []
        config_valid = True
        workspace_available = True

        if self.config:
            settings = self.config.provider_specific_settings or {}
            if settings.get("invalid_config") or (
                self.config.timeout is not None and self.config.timeout <= 0
            ):
                config_valid = False
                errors.append("Invalid adapter configuration or non-positive timeout.")

        if self.project_dir and not self.project_dir.exists():
            workspace_available = False
            errors.append(f"Workspace directory does not exist: {self.project_dir}")

        healthy = config_valid and workspace_available
        msg = (
            f"{self.provider_name} health check passed."
            if healthy
            else f"{self.provider_name} health check failed."
        )

        return HealthCheckResult(
            healthy=healthy,
            configuration_valid=config_valid,
            authenticated=True,
            workspace_available=workspace_available,
            provider_ready=True,
            message=msg,
            errors=errors,
        )

    def execute(self, instruction: str) -> ExecutionResult:
        """Execute a task instruction (not implemented for scaffold adapters)."""
        from core.exceptions import ProviderNotImplementedError

        raise ProviderNotImplementedError(
            f"{type(self).__name__} has no live API integration. "
            "Configure an official API key or automation interface to enable execution."
        )

    def collect_results(self) -> dict[str, Any]:
        """Collect execution telemetry and output paths."""
        return {
            "provider": self.provider_name,
            "contract_path": str(self.task_contract_path)
            if self.task_contract_path
            else None,
            "log_file_path": str(self.log_file_path) if self.log_file_path else None,
            "json_log_path": str(self.json_log_path) if self.json_log_path else None,
            "start_time": self._start_time,
            "end_time": self._end_time,
        }

    def cleanup(self) -> None:
        """Clean up ephemeral handles while preserving logs and contract files."""
        self._log_provider_activity("Cleaning up adapter state.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_configuration(self) -> None:
        """Validate configuration settings (override for provider-specific checks)."""
        if not self.config:
            return
        settings = self.config.provider_specific_settings or {}
        if settings.get("invalid_config"):
            raise ProviderConfigurationError(
                f"Invalid {self.provider_name} provider configuration."
            )

    def _convert_to_contract(self, instruction: str) -> dict[str, Any]:
        """Convert instruction to a standardised contract dictionary."""
        task_id = str(uuid.uuid4())
        tech_stack = {}
        if (
            self.context
            and hasattr(self.context, "architecture")
            and self.context.architecture
        ):
            tech_stack = (
                getattr(self.context.architecture, "technology_stack", {}) or {}
            )

        model_name = (
            self.config.model if self.config else f"{self.provider_name}-default"
        )
        timeout = self.config.timeout if self.config else 30.0

        return {
            "schema_version": "1.0",
            "task_id": task_id,
            "project_name": self.context.project_name if self.context else "unknown",
            "workspace_dir": str(self.project_dir) if self.project_dir else "",
            "task_instruction": instruction,
            "model": model_name,
            "timeout": timeout,
            "acceptance_criteria": [],
            "context": {
                "tech_stack": tech_stack,
            },
            "max_retries": self.config.retries if self.config else 3,
        }

    def load_contract(self) -> dict[str, Any]:
        """Load and validate the task contract file against supported schema versions."""
        if not self.task_contract_path:
            raise ProviderConfigurationError(
                "Task contract path has not been initialized."
            )
        return load_and_validate_contract(self.task_contract_path)

    def _log_provider_activity(self, message: str) -> None:
        """Preserve provider logs separately from execution summaries."""
        if self.log_file_path:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cid = (
                getattr(self.context, "correlation_id", None) if self.context else None
            )
            cid_str = f" [cid:{cid}]" if cid else ""
            log_line = f"[{timestamp}] [{self.provider_name}]{cid_str} {message}\n"
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_line)
