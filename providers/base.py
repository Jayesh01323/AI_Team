"""
Abstract base class for all AI providers.

All providers must implement the AIProvider interface,
returning structured GenerationResult objects instead of raw strings.
"""

from abc import ABC, abstractmethod
from typing import Optional

from models.common import GenerationResult


class AIProvider(ABC):
    """Abstract interface for AI text generation providers."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> GenerationResult:
        """
        Send a prompt to the AI model and return a structured result.

        Args:
            prompt: The input prompt to send to the model.
            max_tokens: Maximum tokens in the response (overrides default).

        Returns:
            A GenerationResult containing the response text and metadata.

        Raises:
            ProviderAuthenticationError: If API key is invalid.
            ProviderRateLimitError: If rate limit is exceeded.
            ProviderError: If generation fails for any other reason.
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """Return the human-readable name of this provider."""
        ...