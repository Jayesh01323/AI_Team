import json

import pytest

from core.exceptions import ProviderConfigurationError
from execution.adapters.contract import (
    DEFAULT_SCHEMA_VERSION,
    SUPPORTED_SCHEMA_VERSIONS,
    load_and_validate_contract,
)
from execution.adapters.openhands import OpenHandsAdapter
from models.project_context import ProjectContext


def test_contract_schema_valid(tmp_path):
    contract_file = tmp_path / "contract.json"
    payload = {"schema_version": "1.0", "task_id": "t-1", "instruction": "Do x"}
    contract_file.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_and_validate_contract(contract_file)
    assert loaded["schema_version"] == "1.0"
    assert loaded["task_id"] == "t-1"


def test_contract_schema_backwards_compatibility_missing_version(tmp_path):
    contract_file = tmp_path / "legacy_contract.json"
    payload = {"task_id": "legacy-1", "instruction": "Legacy task"}
    contract_file.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_and_validate_contract(contract_file)
    assert loaded["schema_version"] == DEFAULT_SCHEMA_VERSION
    assert loaded["task_id"] == "legacy-1"


def test_contract_schema_unsupported_version_raises(tmp_path):
    contract_file = tmp_path / "future_contract.json"
    payload = {"schema_version": "99.0", "task_id": "f-1"}
    contract_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(
        ProviderConfigurationError, match="Unsupported contract schema version: '99.0'"
    ):
        load_and_validate_contract(contract_file)


def test_contract_schema_invalid_file_raises(tmp_path):
    non_existent = tmp_path / "missing.json"
    with pytest.raises(
        ProviderConfigurationError, match="Contract file does not exist"
    ):
        load_and_validate_contract(non_existent)

    invalid_json = tmp_path / "corrupt.json"
    invalid_json.write_text("{invalid json", encoding="utf-8")
    with pytest.raises(
        ProviderConfigurationError, match="Failed to read contract JSON"
    ):
        load_and_validate_contract(invalid_json)


def test_openhands_adapter_schema_validation(tmp_path):
    adapter = OpenHandsAdapter()
    adapter.prepare(ProjectContext(project_name="schema_proj"), tmp_path)

    # 1. Execute creates contract with schema_version 1.0
    adapter.execute("Build task")
    assert adapter.task_contract_path.exists()

    contract = adapter.load_contract()
    assert contract["schema_version"] in SUPPORTED_SCHEMA_VERSIONS

    # 2. Overwrite with unsupported schema_version and verify load_contract raises
    corrupt_payload = contract.copy()
    corrupt_payload["schema_version"] = "2.0"
    adapter.task_contract_path.write_text(json.dumps(corrupt_payload), encoding="utf-8")

    with pytest.raises(
        ProviderConfigurationError, match="Unsupported contract schema version: '2.0'"
    ):
        adapter.load_contract()
