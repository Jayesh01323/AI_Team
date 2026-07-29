import json

import pytest

from core.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderError,
    ProviderExecutionError,
    ProviderRateLimitError,
)
from execution.adapters.openhands import OpenHandsAdapter
from models.architecture import Architecture
from models.execution import AdapterConfiguration
from models.project_context import ProjectContext


def test_openhands_prepare_success(tmp_path):
    adapter = OpenHandsAdapter()
    context = ProjectContext(project_name="my_proj")

    adapter.prepare(context, tmp_path)

    assert adapter.project_dir == tmp_path
    assert adapter.task_contract_path == tmp_path / ".ai" / "openhands_contract.json"
    assert adapter.log_file_path == tmp_path / ".ai" / "logs" / "openhands.log"
    assert (tmp_path / ".ai" / "logs").exists()


def test_openhands_prepare_missing_dir_raises():
    adapter = OpenHandsAdapter()
    non_existent = tmp_path_dummy = Path = None  # noqa: F841

    with pytest.raises(
        ProviderConfigurationError, match="Workspace project_dir cannot be None"
    ):
        adapter.prepare(ProjectContext(project_name="x"), None)


def test_openhands_execute_success(tmp_path):
    config = AdapterConfiguration(
        provider_name="openhands",
        model="claude-3-5-sonnet",
        timeout=60.0,
        retries=2,
    )
    adapter = OpenHandsAdapter(config=config)
    context = ProjectContext(project_name="test_app")
    context.architecture = Architecture(
        system_overview="Web App", technology_stack={"backend": "fastapi"}
    )

    adapter.prepare(context, tmp_path)
    result = adapter.execute("Implement endpoint")

    assert result.status == "SUCCESS"
    assert result.exit_code == 0
    assert result.success is True
    assert "claude-3-5-sonnet" in result.agent_trajectory_summary

    # Check contract content
    assert adapter.task_contract_path.exists()
    with open(adapter.task_contract_path, encoding="utf-8") as f:
        contract = json.load(f)
        assert contract["schema_version"] == "1.0"
        assert contract["model"] == "claude-3-5-sonnet"
        assert contract["timeout"] == 60.0
        assert contract["context"]["tech_stack"] == {"backend": "fastapi"}

    # Check separate log file creation
    assert adapter.log_file_path.exists()
    log_content = adapter.log_file_path.read_text(encoding="utf-8")
    assert "[OpenHands] Starting task execution" in log_content
    assert "[OpenHands] Task execution completed" in log_content


def test_openhands_error_mapping_auth(tmp_path):
    config = AdapterConfiguration(
        provider_name="openhands",
        model="default",
        environment={"OPENHANDS_API_KEY": "INVALID"},
    )
    adapter = OpenHandsAdapter(config=config)
    adapter.prepare(ProjectContext(project_name="test"), tmp_path)

    with pytest.raises(
        ProviderAuthenticationError, match="API key is invalid or unauthorized"
    ):
        adapter.execute("Do work")


def test_openhands_error_mapping_rate_limit(tmp_path):
    config = AdapterConfiguration(
        provider_name="openhands",
        model="default",
        provider_specific_settings={"rate_limit_exceeded": True},
    )
    adapter = OpenHandsAdapter(config=config)
    adapter.prepare(ProjectContext(project_name="test"), tmp_path)

    with pytest.raises(ProviderRateLimitError, match="rate limit exceeded"):
        adapter.execute("Do work")


def test_openhands_error_mapping_config_error(tmp_path):
    config = AdapterConfiguration(
        provider_name="openhands",
        model="default",
        provider_specific_settings={"invalid_config": True},
    )
    adapter = OpenHandsAdapter(config=config)
    adapter.prepare(ProjectContext(project_name="test"), tmp_path)

    with pytest.raises(
        ProviderConfigurationError, match="Invalid OpenHands provider configuration"
    ):
        adapter.execute("Do work")


def test_openhands_error_mapping_general_error(tmp_path):
    config = AdapterConfiguration(
        provider_name="openhands",
        model="default",
        provider_specific_settings={"execution_error": True},
    )
    adapter = OpenHandsAdapter(config=config)
    adapter.prepare(ProjectContext(project_name="test"), tmp_path)

    with pytest.raises(ProviderExecutionError, match="runtime execution failure"):
        adapter.execute("Do work")

    # Verify backwards compatibility (can also be caught as ProviderError)
    with pytest.raises(ProviderError):
        adapter.execute("Do work")


def test_openhands_collect_results_and_cleanup(tmp_path):
    adapter = OpenHandsAdapter()
    adapter.prepare(ProjectContext(project_name="test"), tmp_path)
    adapter.execute("Task instructions")

    results = adapter.collect_results()
    assert results["provider"] == "openhands"
    assert results["contract_path"] == str(adapter.task_contract_path)
    assert results["log_file_path"] == str(adapter.log_file_path)

    adapter.cleanup()
    assert adapter.log_file_path.exists()
