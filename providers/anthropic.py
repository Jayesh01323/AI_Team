"""
Anthropic (Claude) provider implementation.

Not yet implemented. Raises NotImplementedError.
"""

from typing import Optional

from core.exceptions import ProviderNotImplementedError
from models.common import GenerationResult
from providers.base import AIProvider


class AnthropicProvider(AIProvider):
    """Concrete provider for Anthropic Claude models (stub)."""

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> GenerationResult:
        raise ProviderNotImplementedError(
            "Anthropic provider is not yet implemented. "
            "Set AI_PROVIDER=openai or implement providers/anthropic.py."
        )

    def name(self) -> str:
        return "anthropic/claude (not implemented)"