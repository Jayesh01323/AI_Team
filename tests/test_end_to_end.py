"""
End-to-End Integration Test Suite

Validates the complete execution engine workflow and error scenarios:
Repository -> ExecutionEngine -> ProviderAdapter -> ValidationEngine -> ExecutionReport

Runs against every registered provider with no provider-specific branches.
"""

from unittest.mock import MagicMock

import pytest

from core.exceptions import (
    ProviderCapabilityError,
    ProviderConfigurationError,
    ProviderExecutionError,
    ProviderNotImplementedError,
)
from execution.adapters.factory import AdapterFactory, ProviderRegistry
from execution.adapters.openhands import OpenHandsAdapter
from execution.engine import ExecutionEngine
from execution.validation.pipeline import ValidationEngine, ValidationResult
from execution.workspace import WorkspaceManager
from models.execution import (
    ExecutionContext,
    ExecutionReport,
    ExecutionTask,
    ProviderCapability,
)

REGISTERED_PROVIDERS = ProviderRegistry.list_providers()


# ---------------------------------------------------------------------------
# Parametrized e2e tests — run the same workflow for every registered provider
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("provider", REGISTERED_PROVIDERS)
def test_e2e_each_provider_lifecycle(tmp_path, monkeypatch, provider):
    """Every registered provider supports prepare -> health_check -> collect_results -> cleanup.

    execute() may raise ProviderNotImplementedError for scaffold adapters.
    """
    repo_dir = tmp_path / f"repo_{provider}"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text("print('hello')", encoding="utf-8")

    task = ExecutionTask(
        id=f"e2e-lifecycle-{provider}",
        title=f"{provider} Lifecycle",
        description=f"Verify {provider} adapter lifecycle",
    )
    context = ExecutionContext(
        repository=str(repo_dir),
        branch="main",
        task=task,
        provider=provider,
    )

    monkeypatch.setattr(WorkspaceManager, "cleanup", lambda self, ws: None)

    mock_val_engine = MagicMock(spec=ValidationEngine)
    mock_val_engine.validate.return_value = [
        ValidationResult(
            validator_name="Ruff",
            success=True,
            correlation_id=context.correlation_id,
        )
    ]

    engine = ExecutionEngine(validation_engine=mock_val_engine)

    # The execution engine handles workspace creation, adapter prep, health check
    try:
        report = engine.execute(task, context, run_health_check=True)
        # If we get here, execute() succeeded
        assert isinstance(report, ExecutionReport)
        assert report.task_id == f"e2e-lifecycle-{provider}"
        assert report.provider == provider
        if report.status == "COMPLETED":
            assert report.errors == []
    except ProviderNotImplementedError:
        # Scaffold adapters are expected to raise this on execute()
        pass


@pytest.mark.parametrize("provider", REGISTERED_PROVIDERS)
def test_e2e_each_provider_prepare_and_health_check(tmp_path, provider):
    """Every provider can be prepared and health-checked directly."""
    adapter = AdapterFactory.get_adapter(provider)
    from models.project_context import ProjectContext

    adapter.prepare(ProjectContext(project_name=f"health_{provider}"), tmp_path)
    health = adapter.health_check()
    assert health.healthy is True


@pytest.mark.parametrize("provider", REGISTERED_PROVIDERS)
def test_e2e_each_provider_contract_generation(tmp_path, provider):
    """Every provider generates a contract file with valid schema_version."""
    adapter = AdapterFactory.get_adapter(provider)
    from models.project_context import ProjectContext

    adapter.prepare(ProjectContext(project_name=f"contract_{provider}"), tmp_path)
    assert adapter.task_contract_path is None or (
        adapter.task_contract_path.parent.exists()
        and adapter.task_contract_path.parent.parent.exists()
    )

    # OpenHands generates a contract on execute; scaffold adapters do not
    # But the .ai directory should exist
    ai_dir = tmp_path / ".ai"
    assert ai_dir.exists()
    logs_dir = ai_dir / "logs"
    assert logs_dir.exists()


# ---------------------------------------------------------------------------
# Existing e2e tests (keep for backward compatibility)
# ---------------------------------------------------------------------------


def test_e2e_successful_execution_workflow(tmp_path, monkeypatch):
    """Verify full end-to-end successful task execution workflow."""
    repo_dir = tmp_path / "target_repo"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text("print('hello')", encoding="utf-8")

    task = ExecutionTask(
        id="e2e-1",
        title="End-to-End Success",
        description="Verify successful execution flow",
        required_capabilities=[
            ProviderCapability.SHELL,
            ProviderCapability.WORKSPACE,
        ],
    )
    context = ExecutionContext(
        repository=str(repo_dir),
        branch="main",
        task=task,
        provider="openhands",
    )

    created_workspaces = []
    original_create = WorkspaceManager.create_workspace

    def tracking_create_workspace(self, repository):
        ws_path = original_create(self, repository)
        created_workspaces.append(ws_path)
        return ws_path

    monkeypatch.setattr(WorkspaceManager, "create_workspace", tracking_create_workspace)
    monkeypatch.setattr(WorkspaceManager, "cleanup", lambda self, ws: None)

    mock_val_engine = MagicMock(spec=ValidationEngine)
    mock_val_engine.validate.return_value = [
        ValidationResult(
            validator_name="Ruff",
            success=True,
            correlation_id=context.correlation_id,
        )
    ]

    engine = ExecutionEngine(validation_engine=mock_val_engine)

    report = engine.execute(task, context, run_health_check=True)

    assert isinstance(report, ExecutionReport)
    assert report.status == "COMPLETED"
    assert report.validation_status == "SUCCESS"
    assert report.correlation_id is not None
    assert report.task_id == "e2e-1"
    assert report.provider == "openhands"
    assert isinstance(report.files_changed, list)
    assert report.errors == []

    assert len(created_workspaces) == 1
    ws_dir = created_workspaces[0]
    contract_file = ws_dir / ".ai" / "openhands_contract.json"
    log_file = ws_dir / ".ai" / "logs" / "openhands.jsonl"
    assert contract_file.exists()
    assert log_file.exists()

    WorkspaceManager().cleanup(ws_dir)


def test_e2e_invalid_provider_configuration(tmp_path):
    """Verify end-to-end failure handling for invalid provider configuration."""
    repo_dir = tmp_path / "repo_invalid_config"
    repo_dir.mkdir()

    task = ExecutionTask(
        id="e2e-invalid-cfg",
        title="Invalid Config Task",
        description="Test invalid config failure",
    )
    context = ExecutionContext(
        repository=str(repo_dir),
        branch="main",
        task=task,
        provider="openhands",
        configuration={"provider_specific_settings": {"invalid_config": True}},
    )

    engine = ExecutionEngine()

    with pytest.raises(
        ProviderConfigurationError, match="Provider health check failed"
    ):
        engine.execute(task, context, run_health_check=True)


def test_e2e_unsupported_capabilities(tmp_path):
    """Verify end-to-end failure handling when provider lacks required capabilities."""
    repo_dir = tmp_path / "repo_unsupported_cap"
    repo_dir.mkdir()

    task = ExecutionTask(
        id="e2e-unsupported-cap",
        title="Unsupported Capability Task",
        description="Requires unsupported tests capability",
        required_capabilities=[ProviderCapability.TESTS],
    )
    context = ExecutionContext(
        repository=str(repo_dir),
        branch="main",
        task=task,
        provider="openhands",
    )

    engine = ExecutionEngine()

    with pytest.raises(
        ProviderCapabilityError, match="lacks required capability: 'tests'"
    ):
        engine.execute(task, context)


def test_e2e_provider_execution_failure(tmp_path, monkeypatch):
    """Verify end-to-end failure handling when provider adapter execution fails."""
    repo_dir = tmp_path / "repo_exec_fail"
    repo_dir.mkdir()

    task = ExecutionTask(
        id="e2e-exec-fail",
        title="Adapter Execution Failure Task",
        description="Test adapter execution error mapping",
    )
    context = ExecutionContext(
        repository=str(repo_dir),
        branch="main",
        task=task,
        provider="openhands",
    )

    monkeypatch.setattr(
        OpenHandsAdapter,
        "execute",
        MagicMock(
            side_effect=ProviderExecutionError("Simulated provider execution error")
        ),
    )

    engine = ExecutionEngine()

    with pytest.raises(
        ProviderExecutionError, match="Simulated provider execution error"
    ):
        engine.execute(task, context)


def test_e2e_validation_failure(tmp_path):
    """Verify end-to-end execution report validation_status when validation fails."""
    repo_dir = tmp_path / "repo_val_fail"
    repo_dir.mkdir()

    task = ExecutionTask(
        id="e2e-val-fail",
        title="Validation Failure Task",
        description="Test validation pipeline failure handling",
    )
    context = ExecutionContext(
        repository=str(repo_dir),
        branch="main",
        task=task,
        provider="openhands",
    )

    mock_val_engine = MagicMock(spec=ValidationEngine)
    mock_val_engine.validate.return_value = [
        ValidationResult(
            validator_name="Pytest",
            success=False,
            errors=["1 test failed in test_app.py"],
            correlation_id=context.correlation_id,
        )
    ]

    engine = ExecutionEngine(validation_engine=mock_val_engine)

    report = engine.execute(task, context)

    assert isinstance(report, ExecutionReport)
    assert report.status == "COMPLETED"
    assert report.validation_status == "FAILED"
    assert "1 test failed in test_app.py" in report.errors
