import time
import uuid
from datetime import UTC, datetime

from core.exceptions import ProviderConfigurationError
from core.logging import get_logger
from execution.adapters.factory import AdapterFactory, ProviderRegistry
from execution.diff_tracker import WorkspaceDiffTracker
from execution.validation.pipeline import ValidationEngine
from execution.workspace import WorkspaceManager
from models.execution import (
    AdapterConfiguration,
    ExecutionContext,
    ExecutionJob,
    ExecutionReport,
    ExecutionResult,
    ExecutionState,
    ExecutionTask,
    HealthCheckResult,
)
from models.project_context import ProjectContext

logger = get_logger(__name__)


class ExecutionEngine:
    def __init__(
        self,
        workspace_manager: WorkspaceManager | None = None,
        validation_engine: ValidationEngine | None = None,
    ):
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.validation_engine = validation_engine or ValidationEngine()

    def check_provider_health(
        self, provider: str, config: AdapterConfiguration | None = None
    ) -> HealthCheckResult:
        """Standalone provider health check without running any task execution."""
        adapter = AdapterFactory.get_adapter(provider, config)
        return adapter.health_check()

    def execute(
        self,
        task: ExecutionTask,
        context: ExecutionContext,
        run_health_check: bool = False,
    ) -> ExecutionReport:
        """Executes a task end-to-end and returns an ExecutionReport."""
        # 1. Validate inputs
        if not task.id or not task.title or not task.description:
            raise ValueError("Task fields (id, title, description) cannot be empty.")

        if not context.repository:
            raise ValueError("Repository path must be specified.")

        correlation_id = context.correlation_id or str(uuid.uuid4())
        context.correlation_id = correlation_id

        job_id = str(uuid.uuid4())
        job = ExecutionJob(
            id=job_id,
            task=task,
            context=context,
            status=ExecutionState.PENDING,
            created_at=datetime.now(UTC),
            correlation_id=correlation_id,
        )

        start_time = time.time()

        # 2. Prepare workspace
        job.status = ExecutionState.PREPARING
        job.logs.append("Preparing workspace...")
        try:
            workspace_path = self.workspace_manager.create_workspace(context.repository)
            context.workspace = str(workspace_path)
            job.logs.append(f"Workspace prepared at {workspace_path}")
        except Exception as e:
            job.status = ExecutionState.FAILED
            job.logs.append(f"Workspace preparation failed: {e}")
            raise

        # 3. Initialize execution adapter & dispatch
        job.status = ExecutionState.EXECUTING
        job.logs.append(f"Dispatching task to provider adapter: {context.provider}")

        try:
            # Construct AdapterConfiguration if context has configuration details
            config = None
            if context.configuration:
                config = AdapterConfiguration(
                    provider_name=context.provider,
                    model=context.configuration.get("model", "default"),
                    timeout=context.configuration.get("timeout", 30.0),
                    retries=context.configuration.get("retries", 3),
                    environment=context.configuration.get("environment", {}),
                    workspace_options=context.configuration.get(
                        "workspace_options", {}
                    ),
                    provider_specific_settings=context.configuration.get(
                        "provider_specific_settings", {}
                    ),
                )
            # Validate required capabilities before execution
            if task.required_capabilities:
                ProviderRegistry.validate_capabilities(
                    context.provider, task.required_capabilities
                )

            adapter = AdapterFactory.get_adapter(context.provider, config)
            job.adapter = context.provider
        except Exception as e:
            job.status = ExecutionState.FAILED
            job.logs.append(
                f"Failed to load adapter for provider {context.provider}: {e}"
            )
            self.workspace_manager.cleanup(workspace_path)
            raise

        project_context = ProjectContext(project_name=context.repository)

        try:
            adapter.prepare(project_context, workspace_path)
            job.logs.append("Adapter prepared successfully.")

            # Optional health check before execution
            if run_health_check:
                health = adapter.health_check()
                if not health.healthy:
                    err_msg = (
                        f"Provider health check failed: {'; '.join(health.errors)}"
                    )
                    job.logs.append(err_msg)
                    raise ProviderConfigurationError(err_msg)
                job.logs.append("Provider health check passed.")

            # Construct simple instruction
            instruction = f"Task: {task.title}\nDescription: {task.description}"
            if task.requirements:
                instruction += f"\nRequirements: {'; '.join(task.requirements)}"
            if task.acceptance_criteria:
                instruction += (
                    f"\nAcceptance Criteria: {'; '.join(task.acceptance_criteria)}"
                )

            # Snapshot initial workspace state before execution
            diff_tracker = WorkspaceDiffTracker(workspace_path)
            initial_snapshot = diff_tracker.take_snapshot()

            # Dispatch execution to the adapter
            adapter_result = adapter.execute(instruction)
            job.logs.append("Adapter execution completed.")

            # Compute workspace diff post execution
            diff_result = diff_tracker.diff_from_snapshot(initial_snapshot)

            # 4. Collect results & validation
            job.status = ExecutionState.VALIDATING
            job.logs.append("Collecting adapter results...")
            collected_metrics = adapter.collect_results() or {}

            job.logs.append("Running validation pipeline...")
            validation_results = self.validation_engine.validate(
                workspace_path, correlation_id=correlation_id
            )
            validation_success = all(r.success for r in validation_results)
            validation_errors = []
            for r in validation_results:
                if not r.success:
                    validation_errors.extend(r.errors)

            # Derive added/modified/deleted/changed files safely (supporting legacy adapters and test mocks)
            raw_added = getattr(adapter_result, "added_files", None)
            added_files = (
                raw_added
                if isinstance(raw_added, list) and raw_added
                else diff_result.added_files
            )

            raw_modified = getattr(adapter_result, "modified_files", None)
            raw_files_modified = getattr(adapter_result, "files_modified", None)
            if isinstance(raw_modified, list) and raw_modified:
                modified_files = raw_modified
            elif isinstance(raw_files_modified, list) and raw_files_modified:
                modified_files = raw_files_modified
            else:
                modified_files = diff_result.modified_files

            raw_deleted = getattr(adapter_result, "deleted_files", None)
            deleted_files = (
                raw_deleted
                if isinstance(raw_deleted, list) and raw_deleted
                else diff_result.deleted_files
            )

            raw_changed = getattr(adapter_result, "files_changed", None)
            if isinstance(raw_changed, list) and raw_changed:
                files_changed = raw_changed
            elif diff_result.files_changed:
                files_changed = diff_result.files_changed
            else:
                files_changed = sorted(set(added_files + modified_files))




            # Construct ExecutionResult
            success = adapter_result.exit_code == 0 and validation_success
            result = ExecutionResult(
                task_id=task.id,
                status=adapter_result.status,
                files_modified=modified_files,
                added_files=added_files,
                modified_files=modified_files,
                deleted_files=deleted_files,
                agent_trajectory_summary=adapter_result.agent_trajectory_summary,
                error_log=adapter_result.error_log,
                exit_code=adapter_result.exit_code,
                success=success,
                files_changed=files_changed,
                commands_executed=[],
                validation="SUCCESS" if validation_success else "FAILED",
                metrics=collected_metrics,
                errors=validation_errors
                + ([adapter_result.error_log] if adapter_result.error_log else []),
                correlation_id=adapter_result.correlation_id or correlation_id,
            )

            job.result = result
            job.validation_status = result.validation

            job.status = ExecutionState.COMPLETED
            job.completed_at = datetime.now(UTC)
            job.logs.append("Job execution completed successfully.")

        except Exception as e:
            job.status = ExecutionState.FAILED
            job.logs.append(f"Adapter execution failed: {e}")
            raise
        finally:
            # Cleanup workspace
            try:
                adapter.cleanup()
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error cleaning up adapter: {e}")
            self.workspace_manager.cleanup(workspace_path)

        end_time = time.time()
        duration = end_time - start_time

        # 5. Create ExecutionReport
        report = ExecutionReport(
            job_id=job.id,
            provider=context.provider,
            task_id=task.id,
            status=job.status.value,
            timing=duration,
            files_changed=result.files_changed,
            added_files=result.added_files,
            modified_files=result.modified_files,
            deleted_files=result.deleted_files,
            commands_executed=result.commands_executed,
            validation_status=result.validation,
            errors=result.errors,
            correlation_id=correlation_id,
        )


        return report
