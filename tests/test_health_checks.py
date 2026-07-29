from unittest.mock import MagicMock

import pytest

from core.exceptions import ProviderConfigurationError
from execution.adapters.openhands import OpenHandsAdapter
from execution.engine import ExecutionEngine
from models.execution import AdapterConfiguration, ExecutionContext, ExecutionTask
from models.project_context import ProjectContext


def test_openhands_adapter_health_check_healthy(tmp_path):
    adapter = OpenHandsAdapter()
    adapter.prepare(ProjectContext(project_name="health_test"), tmp_path)

    res = adapter.health_check()
    assert res.healthy is True
    assert res.configuration_valid is True
    assert res.authenticated is True
    assert res.workspace_available is True
    assert res.provider_ready is True
    assert res.errors == []


def test_openhands_adapter_health_check_unhealthy(tmp_path):
    config = AdapterConfiguration(
        provider_name="openhands",
        model="default",
        environment={"OPENHANDS_API_KEY": "INVALID"},
        provider_specific_settings={"invalid_config": True, "unhealthy": True},
    )
    adapter = OpenHandsAdapter(config=config)
    adapter.prepare(ProjectContext(project_name="health_test_err"), tmp_path)

    res = adapter.health_check()
    assert res.healthy is False
    assert res.configuration_valid is False
    assert res.authenticated is False
    assert res.provider_ready is False
    assert len(res.errors) >= 3


def test_engine_check_provider_health():
    engine = ExecutionEngine()
    health = engine.check_provider_health("openhands")
    assert health.healthy is True


def test_engine_execute_with_health_check_success(tmp_path):
    task = ExecutionTask(id="h-1", title="Health Task", description="Desc")
    context = ExecutionContext(
        repository=str(tmp_path), branch="main", task=task, provider="openhands"
    )

    mock_workspace_mgr = MagicMock()
    mock_workspace_mgr.create_workspace.return_value = tmp_path

    mock_val_engine = MagicMock()
    mock_val_engine.validate.return_value = []

    engine = ExecutionEngine(
        workspace_manager=mock_workspace_mgr, validation_engine=mock_val_engine
    )
    report = engine.execute(task, context, run_health_check=True)
    assert report.status == "COMPLETED"


def test_engine_execute_with_health_check_failure_aborts(tmp_path):
    task = ExecutionTask(id="h-2", title="Unhealthy Task", description="Desc")
    context = ExecutionContext(
        repository=str(tmp_path),
        branch="main",
        task=task,
        provider="openhands",
        configuration={"provider_specific_settings": {"invalid_config": True}},
    )

    mock_workspace_mgr = MagicMock()
    mock_workspace_mgr.create_workspace.return_value = tmp_path

    engine = ExecutionEngine(workspace_manager=mock_workspace_mgr)
    with pytest.raises(
        ProviderConfigurationError, match="Provider health check failed"
    ):
        engine.execute(task, context, run_health_check=True)
