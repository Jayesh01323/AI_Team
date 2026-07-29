from unittest.mock import MagicMock

import pytest

from core.exceptions import (
    ProviderCapabilityError,
    ProviderConfigurationError,
    ProviderError,
    ProviderExecutionError,
    ProviderNotRegisteredError,
)
from execution.adapters.base import ExecutionAdapter
from execution.adapters.factory import AdapterFactory, ProviderRegistry
from models.execution import AdapterConfiguration, ProviderCapabilities


class DummyTestAdapter(ExecutionAdapter):
    def prepare(self, context, project_dir):
        pass

    def execute(self, instruction):
        return MagicMock()

    def collect_results(self):
        return {}

    def cleanup(self):
        pass


def test_provider_registration_lifecycle():
    # Test registration
    capabilities = ProviderCapabilities(
        provider_name="test_dummy", supports_images=True
    )
    ProviderRegistry.register_provider("test_dummy", DummyTestAdapter, capabilities)

    assert ProviderRegistry.has_provider("test_dummy") is True
    assert "test_dummy" in ProviderRegistry.list_providers()

    # Test capability lookup
    adapter_cls, caps = ProviderRegistry.get_provider("test_dummy")
    assert adapter_cls == DummyTestAdapter
    assert caps.supports_images is True

    # Test duplicate registration rejection
    with pytest.raises(ValueError, match="already registered"):
        ProviderRegistry.register_provider("test_dummy", DummyTestAdapter, capabilities)

    # Test unregister
    ProviderRegistry.unregister_provider("test_dummy")
    assert ProviderRegistry.has_provider("test_dummy") is False


def test_missing_provider_raises():
    with pytest.raises(ProviderNotRegisteredError):
        ProviderRegistry.get_provider("non_existent_provider")

    with pytest.raises(ProviderNotRegisteredError):
        AdapterFactory.get_adapter("non_existent_provider")


def test_factory_creation_and_config():
    capabilities = ProviderCapabilities(provider_name="test_config_prov")
    ProviderRegistry.register_provider(
        "test_config_prov", DummyTestAdapter, capabilities
    )

    try:
        # Success creation without config
        adapter = AdapterFactory.get_adapter("test_config_prov")
        assert isinstance(adapter, DummyTestAdapter)

        # Success creation with valid config
        config = AdapterConfiguration(
            provider_name="test_config_prov", model="gpt-4", timeout=10.0, retries=2
        )
        adapter_with_config = AdapterFactory.get_adapter("test_config_prov", config)
        assert adapter_with_config.config == config

        # Failure: Name mismatch
        wrong_name_config = AdapterConfiguration(
            provider_name="other_prov", model="gpt-4"
        )
        with pytest.raises(ProviderConfigurationError, match="provider name mismatch"):
            AdapterFactory.get_adapter("test_config_prov", wrong_name_config)

        # Failure: Invalid timeout
        invalid_timeout_config = AdapterConfiguration(
            provider_name="test_config_prov", model="gpt-4", timeout=-1.0
        )
        with pytest.raises(
            ProviderConfigurationError, match="Timeout must be positive"
        ):
            AdapterFactory.get_adapter("test_config_prov", invalid_timeout_config)

        # Failure: Invalid retries
        invalid_retries_config = AdapterConfiguration(
            provider_name="test_config_prov", model="gpt-4", retries=-1
        )
        with pytest.raises(
            ProviderConfigurationError, match="Retries cannot be negative"
        ):
            AdapterFactory.get_adapter("test_config_prov", invalid_retries_config)

    finally:
        ProviderRegistry.unregister_provider("test_config_prov")


def test_exception_hierarchy():
    # Verify inheritance
    assert issubclass(ProviderNotRegisteredError, ProviderError)
    assert issubclass(ProviderConfigurationError, ProviderError)
    assert issubclass(ProviderCapabilityError, ProviderError)
    assert issubclass(ProviderExecutionError, ProviderError)
