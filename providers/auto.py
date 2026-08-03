"""
Auto-failover provider implementation.

Tries Gemini first, and automatically falls back to NVIDIA if Gemini
returns rate limit (429), quota exhausted, or temporary service errors.
"""

from core.exceptions import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
)
from core.logging import get_logger
from models.common import GenerationResult
from providers.base import AIProvider
from providers.gemini import GeminiProvider
from providers.nvidia import NvidiaProvider

logger = get_logger(__name__)


class AutoProvider(AIProvider):
    """Provider wrapper implementing automatic failover (Gemini -> NVIDIA)."""

    def __init__(
        self,
        primary: AIProvider | None = None,
        secondary: AIProvider | None = None,
    ) -> None:
        self._primary = primary or GeminiProvider()
        self._secondary = secondary or NvidiaProvider()

    def generate(self, prompt: str, max_tokens: int | None = None) -> GenerationResult:
        """
        Attempt generation using primary provider, falling back to secondary on
        rate limits or temporary service unavailability.
        """
        try:
            return self._primary.generate(prompt, max_tokens=max_tokens)
        except (ProviderRateLimitError, ProviderError) as exc:
            # Do NOT switch on authentication failures
            if isinstance(exc, ProviderAuthenticationError):
                raise

            err_str = str(exc).lower()
            is_transient = (
                isinstance(exc, ProviderRateLimitError)
                or "rate limit" in err_str
                or "quota" in err_str
                or "429" in err_str
                or "503" in err_str
                or "502" in err_str
                or "service unavailable" in err_str
                or "temporarily unavailable" in err_str
            )

            if not is_transient:
                raise

            logger.warning(
                "Primary provider '%s' failed with transient error: %s. Falling back to '%s'.",
                self._primary.name(),
                exc,
                self._secondary.name(),
            )

            try:
                return self._secondary.generate(prompt, max_tokens=max_tokens)
            except Exception as sec_exc:
                logger.error(
                    "Secondary provider '%s' also failed: %s",
                    self._secondary.name(),
                    sec_exc,
                )
                raise ProviderError(
                    f"Auto mode failover failed. Primary ('{self._primary.name()}') error: {exc}. "
                    f"Secondary ('{self._secondary.name()}') error: {sec_exc}"
                ) from sec_exc

    def name(self) -> str:
        return f"auto ({self._primary.name()} -> {self._secondary.name()})"
