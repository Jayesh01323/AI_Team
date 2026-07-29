import json

import pytest

from core.exceptions import (
    ProviderNotImplementedError,
    ProviderNotRegisteredError,
)
from execution.adapters.factory import AdapterFactory
from models.architecture import Architecture
from models.project_context import ProjectContext


def test_adapter_factory():
    adapter = AdapterFactory.get_adapter("openhands")
    assert adapter.__class__.__name__ == "OpenHandsAdapter"

    adapter2 = AdapterFactory.get_adapter("claude")
    assert adapter2.__class__.__name__ == "ClaudeAdapter"

    with pytest.raises(ProviderNotRegisteredError):
        AdapterFactory.get_adapter("unknown")


def test_openhands_adapter(tmp_path):
    adapter = AdapterFactory.get_adapter("openhands")
    context = ProjectContext(project_name="test_project")
    context.architecture = Architecture(
        system_overview="Test", technology_stack={"backend": "fastapi"}
    )

    adapter.prepare(context, tmp_path)
    assert adapter.task_contract_path == tmp_path / ".ai" / "openhands_contract.json"

    result = adapter.execute("Implement login")

    assert result.status == "SUCCESS"
    assert result.exit_code == 0

    # Verify contract was written
    assert adapter.task_contract_path.exists()

    with open(adapter.task_contract_path) as f:
        contract = json.load(f)
        assert contract["project_name"] == "test_project"
        assert contract["task_instruction"] == "Implement login"
        assert contract["context"]["tech_stack"] == {"backend": "fastapi"}


SCAFFOLD_PROVIDERS = ("claude", "codex", "devin", "antigravity", "cursor", "vscode")


def test_scaffold_adapters():
    """Scaffold adapters have working lifecycle but execute() raises ProviderNotImplementedError."""
    for name in SCAFFOLD_PROVIDERS:
        adapter = AdapterFactory.get_adapter(name)
        assert adapter.__class__.__name__.endswith("Adapter")

        # prepare, collect_results, cleanup, health_check all work
        assert callable(adapter.prepare)
        assert callable(adapter.collect_results)
        assert callable(adapter.cleanup)
        assert callable(adapter.health_check)

        # Only execute raises ProviderNotImplementedError
        with pytest.raises(ProviderNotImplementedError):
            adapter.execute("")


def test_scaffold_adapters_do_not_raise_bare_not_implemented_error():
    """Ensure scaffold adapters never raise bare NotImplementedError."""
    for name in SCAFFOLD_PROVIDERS:
        adapter = AdapterFactory.get_adapter(name)
        try:
            adapter.execute("")
        except ProviderNotImplementedError:
            pass  # Expected
        except NotImplementedError:
            pytest.fail(
                f"{name} adapter raised bare NotImplementedError instead of ProviderNotImplementedError"
            )


def test_scaffold_adapters_prepare_and_health_check(tmp_path):
    """Scaffold adapters can prepare and perform health checks with a valid workspace."""
    for name in SCAFFOLD_PROVIDERS:
        adapter = AdapterFactory.get_adapter(name)
        context = ProjectContext(project_name=f"test_{name}")
        adapter.prepare(context, tmp_path)
        assert adapter.task_contract_path is not None
        assert adapter.log_file_path is not None

        health = adapter.health_check()
        assert health.healthy is True

        results = adapter.collect_results()
        assert results["provider"] == name

        adapter.cleanup()
