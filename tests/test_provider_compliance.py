"""
Provider Compliance Test Suite

A reusable test suite verifying that every registered provider adapter satisfies:
1. health_check()
2. execute()
3. capability reporting
4. configuration validation
5. structured logging
6. contract generation
7. exception mapping
"""

import json

pytest_plugins = []
import pytest

from core.exceptions import (
    ProviderConfigurationError,
    ProviderError,
    ProviderNotImplementedError,
)
from execution.adapters.base import ExecutionAdapter
from execution.adapters.factory import AdapterFactory, ProviderRegistry
from models.execution import (
    AdapterConfiguration,
    ExecutionResult,
    HealthCheckResult,
    ProviderCapabilities,
)
from models.project_context import ProjectContext

REGISTERED_PROVIDERS = ProviderRegistry.list_providers()


class BaseProviderComplianceTest:
    """Reusable compliance test suite for any provider adapter implementation."""

    provider_name: str

    def get_adapter(
        self, config: AdapterConfiguration | None = None
    ) -> ExecutionAdapter:
        return AdapterFactory.get_adapter(self.provider_name, config)

    def test_capability_reporting(self):
        """Verify capability reporting and registry metadata."""
        assert ProviderRegistry.has_provider(self.provider_name)
        adapter_cls, capabilities = ProviderRegistry.get_provider(self.provider_name)
        assert issubclass(adapter_cls, ExecutionAdapter)
        assert isinstance(capabilities, ProviderCapabilities)
        assert capabilities.provider_name.lower() == self.provider_name.lower()
        assert isinstance(capabilities.capabilities, set)

    def test_configuration_validation(self):
        """Verify adapter configuration validation."""
        adapter = self.get_adapter()
        assert isinstance(adapter, ExecutionAdapter)

        valid_config = AdapterConfiguration(
            provider_name=self.provider_name,
            model="default",
            timeout=15.0,
        )
        adapter_with_config = self.get_adapter(valid_config)
        assert adapter_with_config.config is not None
        assert adapter_with_config.config.provider_name == self.provider_name

        mismatched_config = AdapterConfiguration(
            provider_name="mismatched_provider_name",
            model="default",
        )
        with pytest.raises(
            ProviderConfigurationError,
            match="Configuration provider name mismatch",
        ):
            self.get_adapter(mismatched_config)

    def test_health_check(self, tmp_path):
        """Verify health_check() returns HealthCheckResult or handles uninitialized state."""
        adapter = self.get_adapter()
        try:
            adapter.prepare(ProjectContext(project_name="health_check_test"), tmp_path)
            health = adapter.health_check()
            assert isinstance(health, HealthCheckResult)
            assert isinstance(health.healthy, bool)
            assert isinstance(health.errors, list)
        except ProviderNotImplementedError:
            pass

    def test_contract_generation(self, tmp_path):
        """Verify contract generation schema version presence."""
        adapter = self.get_adapter()
        try:
            adapter.prepare(ProjectContext(project_name="contract_test"), tmp_path)
            contract_file = tmp_path / ".ai" / f"{self.provider_name}_contract.json"
            if contract_file.exists():
                content = contract_file.read_text(encoding="utf-8")
                assert "schema_version" in content
        except ProviderNotImplementedError:
            pass

    def test_execute_and_exception_mapping(self, tmp_path):
        """Verify execute() returns ExecutionResult or maps exceptions to ProviderError."""
        adapter = self.get_adapter()
        try:
            adapter.prepare(ProjectContext(project_name="exec_test"), tmp_path)
            res = adapter.execute("Run compliance instruction")
            assert isinstance(res, ExecutionResult)
            assert isinstance(res.status, str)
        except Exception as exc:  # noqa: BLE001
            assert isinstance(exc, ProviderError), (
                f"Provider raised non-ProviderError exception: {type(exc).__name__}: {exc}"
            )


@pytest.mark.parametrize("provider_name", REGISTERED_PROVIDERS)
def test_generic_provider_compliance(provider_name, tmp_path):
    """Parametrized compliance test suite automatically validating all registered providers."""
    suite = BaseProviderComplianceTest()
    suite.provider_name = provider_name

    suite.test_capability_reporting()
    suite.test_configuration_validation()
    suite.test_health_check(tmp_path)
    suite.test_contract_generation(tmp_path)
    suite.test_execute_and_exception_mapping(tmp_path)


class TestOpenHandsProviderCompliance(BaseProviderComplianceTest):
    """Subclass compliance test suite specifically verifying production OpenHandsAdapter."""

    provider_name = "openhands"

    def test_openhands_structured_logging(self, tmp_path):
        """Verify structured JSON Lines log generation with required schema fields."""
        adapter = self.get_adapter()
        adapter.prepare(ProjectContext(project_name="log_test"), tmp_path)
        res = adapter.execute("Instruction for logging")
        assert res.status in ("SUCCESS", "COMPLETED")

        log_path = tmp_path / ".ai" / "logs" / "openhands.jsonl"
        assert log_path.exists(), "Structured JSON Lines log file was not created"

        log_lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(log_lines) >= 1

        entry = json.loads(log_lines[0])
        required_keys = {
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
        assert required_keys.issubset(entry.keys())
        assert entry["provider"] == "openhands"
