import json

import pytest

from core.exceptions import ProviderAuthenticationError
from execution.adapters.logger import ProviderStructuredLogger
from execution.adapters.openhands import OpenHandsAdapter
from models.execution import AdapterConfiguration
from models.project_context import ProjectContext


def test_structured_logger_schema_fields(tmp_path):
    log_file = tmp_path / "test.jsonl"
    logger = ProviderStructuredLogger(log_file)

    entry = logger.log(
        provider="test_provider",
        model="gpt-4o",
        task_id="t-100",
        execution_id="e-200",
        status="SUCCESS",
        duration_ms=150.5,
        error=None,
    )

    assert entry.provider == "test_provider"
    assert entry.status == "SUCCESS"

    # Read lines and verify JSON structure and required keys
    entries = logger.read_entries()
    assert len(entries) == 1
    log_dict = entries[0]

    required_fields = {
        "timestamp",
        "provider",
        "model",
        "task_id",
        "execution_id",
        "status",
        "duration_ms",
        "error",
        "correlation_id",
    }
    assert set(log_dict.keys()) == required_fields
    assert log_dict["provider"] == "test_provider"
    assert log_dict["model"] == "gpt-4o"
    assert log_dict["task_id"] == "t-100"
    assert log_dict["execution_id"] == "e-200"
    assert log_dict["status"] == "SUCCESS"
    assert log_dict["duration_ms"] == 150.5
    assert log_dict["error"] is None


def test_openhands_adapter_structured_logging_success(tmp_path):
    adapter = OpenHandsAdapter()
    adapter.prepare(ProjectContext(project_name="logging_app"), tmp_path)

    adapter.execute("Build component")

    assert adapter.json_log_path.exists()
    with open(adapter.json_log_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        assert len(lines) == 1
        record = json.loads(lines[0])

    required_fields = {
        "timestamp",
        "provider",
        "model",
        "task_id",
        "execution_id",
        "status",
        "duration_ms",
        "error",
        "correlation_id",
    }
    assert set(record.keys()) == required_fields
    assert record["provider"] == "openhands"
    assert record["status"] == "SUCCESS"
    assert record["error"] is None


def test_openhands_adapter_structured_logging_error(tmp_path):
    config = AdapterConfiguration(
        provider_name="openhands",
        model="gpt-4",
        provider_specific_settings={"auth_error": True},
    )
    adapter = OpenHandsAdapter(config=config)
    adapter.prepare(ProjectContext(project_name="logging_err_app"), tmp_path)

    with pytest.raises(ProviderAuthenticationError):
        adapter.execute("Do failed work")

    assert adapter.json_log_path.exists()
    with open(adapter.json_log_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        assert len(lines) == 1
        record = json.loads(lines[0])

    assert record["provider"] == "openhands"
    assert record["status"] == "FAILED"
    assert record["error"] == "OpenHands API key is invalid or unauthorized."
