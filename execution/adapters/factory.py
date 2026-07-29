from typing import ClassVar

from core.exceptions import (
    ProviderCapabilityError,
    ProviderConfigurationError,
    ProviderNotRegisteredError,
)
from execution.adapters.antigravity import AntigravityAdapter
from execution.adapters.base import ExecutionAdapter
from execution.adapters.claude import ClaudeAdapter
from execution.adapters.codex import CodexAdapter
from execution.adapters.cursor import CursorAdapter
from execution.adapters.devin import DevinAdapter
from execution.adapters.openhands import OpenHandsAdapter
from execution.adapters.vscode import VSCodeAdapter
from models.execution import (
    AdapterConfiguration,
    ProviderCapabilities,
    ProviderCapability,
)


class ProviderRegistry:
    _registry: ClassVar[
        dict[str, tuple[type[ExecutionAdapter], ProviderCapabilities]]
    ] = {}

    @classmethod
    def register_provider(
        cls,
        provider_name: str,
        adapter_class: type[ExecutionAdapter],
        capabilities: ProviderCapabilities,
    ) -> None:
        name = provider_name.lower()
        if name in cls._registry:
            raise ValueError(f"Provider '{provider_name}' is already registered.")
        cls._registry[name] = (adapter_class, capabilities)

    @classmethod
    def unregister_provider(cls, provider_name: str) -> None:
        name = provider_name.lower()
        if name not in cls._registry:
            raise ProviderNotRegisteredError(
                f"Provider '{provider_name}' is not registered."
            )
        del cls._registry[name]

    @classmethod
    def get_provider(
        cls, provider_name: str
    ) -> tuple[type[ExecutionAdapter], ProviderCapabilities]:
        name = provider_name.lower()
        if name not in cls._registry:
            raise ProviderNotRegisteredError(
                f"Provider '{provider_name}' is not registered."
            )
        return cls._registry[name]

    @classmethod
    def list_providers(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def has_provider(cls, provider_name: str) -> bool:
        return provider_name.lower() in cls._registry

    @classmethod
    def validate_capabilities(
        cls,
        provider_name: str,
        required_capabilities: list[ProviderCapability | str],
    ) -> None:
        if not required_capabilities:
            return
        _, capabilities = cls.get_provider(provider_name)
        for cap in required_capabilities:
            if not capabilities.has_capability(cap):
                cap_str = cap.value if isinstance(cap, ProviderCapability) else cap
                raise ProviderCapabilityError(
                    f"Provider '{capabilities.provider_name}' lacks required capability: '{cap_str}'"
                )


class AdapterFactory:
    @staticmethod
    def get_adapter(
        provider_name: str, config: AdapterConfiguration | None = None
    ) -> ExecutionAdapter:
        # Verify provider registration and get class
        adapter_class, _ = ProviderRegistry.get_provider(provider_name)

        # Validate configuration if provided
        if config is not None:
            if config.provider_name.lower() != provider_name.lower():
                raise ProviderConfigurationError(
                    "Configuration provider name mismatch."
                )
            if config.timeout <= 0:
                raise ProviderConfigurationError("Timeout must be positive.")
            if config.retries < 0:
                raise ProviderConfigurationError("Retries cannot be negative.")

        # Instantiate adapter
        adapter = adapter_class()

        # Inject configuration if present
        if config is not None:
            adapter.config = config

        return adapter


# Explicitly register deterministic stubs on application startup
ProviderRegistry.register_provider(
    "openhands",
    OpenHandsAdapter,
    ProviderCapabilities(
        provider_name="openhands",
        supports_workspace=True,
        supports_shell=True,
        max_context=8192,
    ),
)

ProviderRegistry.register_provider(
    "claude",
    ClaudeAdapter,
    ProviderCapabilities(
        provider_name="claude",
        supports_streaming=True,
        supports_workspace=True,
        max_context=200000,
    ),
)

ProviderRegistry.register_provider(
    "codex",
    CodexAdapter,
    ProviderCapabilities(
        provider_name="codex",
        max_context=4096,
    ),
)

ProviderRegistry.register_provider(
    "devin",
    DevinAdapter,
    ProviderCapabilities(
        provider_name="devin",
        supports_workspace=True,
        supports_shell=True,
        supports_tests=True,
        max_context=32768,
    ),
)

ProviderRegistry.register_provider(
    "antigravity",
    AntigravityAdapter,
    ProviderCapabilities(
        provider_name="antigravity",
        max_context=8192,
    ),
)

ProviderRegistry.register_provider(
    "cursor",
    CursorAdapter,
    ProviderCapabilities(
        provider_name="cursor",
        supports_workspace=True,
        max_context=32768,
    ),
)

ProviderRegistry.register_provider(
    "vscode",
    VSCodeAdapter,
    ProviderCapabilities(
        provider_name="vscode",
        supports_workspace=True,
        supports_shell=True,
        max_context=64000,
    ),
)
