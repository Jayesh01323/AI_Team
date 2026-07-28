"""
Application-layer service for AI provider operations.

CLI commands call this service. The service calls the provider factory.
This keeps the CLI independent of provider implementation details.
"""

from core.config import validate as validate_config
from core.exceptions import ConfigurationError, ProviderError
from core.logging import get_logger
from models.common import GenerationResult
from providers.factory import create_provider

logger = get_logger(__name__)


def test_provider() -> GenerationResult:
    """
    Verify the configured AI provider can return a response.

    Sends a simple prompt and returns the structured result.

    Returns:
        A GenerationResult with the provider's response.

    Raises:
        ConfigurationError: If configuration is invalid.
        ProviderError: If the provider fails to generate.
    """
    issues = validate_config()
    if issues:
        raise ConfigurationError(
            "Configuration validation failed:\n  - " + "\n  - ".join(issues)
        )

    provider = create_provider()
    logger.info("Testing provider: %s", provider.name())

    try:
        result = provider.generate("Reply with exactly: OK. Do not add anything else.")
    except ProviderError:
        raise
    except Exception as exc:
        raise ProviderError(f"Unexpected error testing provider: {exc}") from exc

    logger.info("Provider test succeeded: %s", result.text)
    return result
