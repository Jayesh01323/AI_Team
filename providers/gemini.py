"""
Google Gemini provider implementation.

Not yet implemented. Raises NotImplementedError.
"""

from typing import Optional

from core.exceptions import ProviderNotImplementedError
from models.common import GenerationResult
from providers.base import AIProvider


class GeminiProvider(AIProvider):
    """Concrete provider for Google Gemini models (stub)."""

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> GenerationResult:
        raise ProviderNotImplementedError(
            "Gemini provider is not yet implemented. "
            "Set AI_PROVIDER=openai or implement providers/gemini.py."
        )

    def name(self) -> str:
        return "gemini/gemini-pro (not implemented)"