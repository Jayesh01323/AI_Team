"""
Provider factory — creates the correct AIProvider based on configuration.

CLI and application code never instantiate providers directly.
They always go through this factory.
"""

from core.config import AI_PROVIDER
from core.exceptions import ConfigurationError
from providers.base import AIProvider


def create_provider() -> AIProvider:
    """
    Create and return the configured AI provider.

    Reads AI_PROVIDER from config to determine which provider to instantiate.

    Returns:
        An instance of AIProvider (OpenAIProvider, AnthropicProvider, etc.).

    Raises:
        ConfigurationError: If AI_PROVIDER is set to an unknown value.
    """
    if AI_PROVIDER == "openai":
        from providers.openai import OpenAIProvider

        return OpenAIProvider()

    if AI_PROVIDER == "anthropic":
        from providers.anthropic import AnthropicProvider

        return AnthropicProvider()

    if AI_PROVIDER == "gemini":
        from providers.gemini import GeminiProvider

        return GeminiProvider()

    raise ConfigurationError(
        f"Unknown AI_PROVIDER: '{AI_PROVIDER}'. "
        f"Expected one of: openai, anthropic, gemini."
    )
