from unittest.mock import MagicMock

import pytest

from core.exceptions import ProviderCapabilityError
from execution.adapters.factory import ProviderRegistry
from execution.engine import ExecutionEngine
from models.execution import ExecutionContext, ExecutionTask, ProviderCapability


def test_provider_registry_capability_validation_enum_success():
    # OpenHands supports SHELL and WORKSPACE
    ProviderRegistry.validate_capabilities(
        "openhands", [ProviderCapability.SHELL, ProviderCapability.WORKSPACE]
    )


def test_provider_registry_capability_validation_string_backwards_compat():
    # String capability input works for backward compatibility
    ProviderRegistry.validate_capabilities("openhands", ["shell", "workspace"])


def test_provider_registry_capability_validation_failure():
    # OpenHands does not support TESTS capability by default
    with pytest.raises(
        ProviderCapabilityError, match="lacks required capability: 'tests'"
    ):
        ProviderRegistry.validate_capabilities("openhands", [ProviderCapability.TESTS])


def test_execution_engine_capability_validation_rejection(tmp_path):
    task = ExecutionTask(
        id="cap-1",
        title="Testing Task",
        description="Requires test support",
        required_capabilities=[ProviderCapability.TESTS],
    )
    context = ExecutionContext(
        repository=str(tmp_path),
        branch="main",
        task=task,
        provider="openhands",
    )

    mock_workspace_mgr = MagicMock()
    mock_workspace_mgr.create_workspace.return_value = tmp_path

    engine = ExecutionEngine(workspace_manager=mock_workspace_mgr)

    with pytest.raises(
        ProviderCapabilityError, match="lacks required capability: 'tests'"
    ):
        engine.execute(task, context)


def test_execution_engine_capability_validation_success(tmp_path):
    task = ExecutionTask(
        id="cap-2",
        title="Shell Task",
        description="Requires shell and workspace",
        required_capabilities=[
            ProviderCapability.SHELL,
            ProviderCapability.WORKSPACE,
        ],
    )
    context = ExecutionContext(
        repository=str(tmp_path),
        branch="main",
        task=task,
        provider="openhands",
    )

    mock_workspace_mgr = MagicMock()
    mock_workspace_mgr.create_workspace.return_value = tmp_path

    mock_val_engine = MagicMock()
    mock_val_engine.validate.return_value = []

    engine = ExecutionEngine(
        workspace_manager=mock_workspace_mgr, validation_engine=mock_val_engine
    )

    report = engine.execute(task, context)
    assert report.status == "COMPLETED"
