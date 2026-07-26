"""
OpenAI provider implementation.

Requires OPENAI_API_KEY environment variable.
Uses the OpenAI Python SDK under the hood.
"""

from typing import Optional

from core.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from core.exceptions import ProviderAuthenticationError, ProviderError
from core.logging import get_logger
from models.common import GenerationResult
from providers.base import AIProvider

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    """Concrete provider for OpenAI models (GPT-4, GPT-4o, etc.)."""

    def __init__(self) -> None:
        self._model = OPENAI_MODEL
        self._max_tokens = OPENAI_MAX_TOKENS
        self._temperature = OPENAI_TEMPERATURE
        self._client = None

    def _get_client(self):
        """Lazily initialize the OpenAI client (avoids import if not used)."""
        if self._client is not None:
            return self._client

        if not OPENAI_API_KEY:
            raise ProviderAuthenticationError(
                "OPENAI_API_KEY is not set. "
                "Set it in your environment or .env file."
            )

        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=OPENAI_API_KEY)
        except ImportError:
            raise ProviderError(
                "OpenAI SDK is not installed. Run: pip install openai"
            )
        except Exception as exc:
            raise ProviderAuthenticationError(
                f"Failed to initialize OpenAI client: {exc}"
            )

        return self._client

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> GenerationResult:
        client = self._get_client()
        token_limit = max_tokens or self._max_tokens

        logger.debug(
            "OpenAI generate: model=%s max_tokens=%d temperature=%.1f",
            self._model, token_limit, self._temperature,
        )

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=token_limit,
                temperature=self._temperature,
            )
        except Exception as exc:
            error_msg = str(exc).lower()
            if "authentication" in error_msg or "api key" in error_msg:
                raise ProviderAuthenticationError(
                    f"OpenAI authentication failed: {exc}"
                )
            if "rate limit" in error_msg or "too many" in error_msg:
                from core.exceptions import ProviderRateLimitError
                raise ProviderRateLimitError(
                    f"OpenAI rate limit exceeded: {exc}"
                )
            raise ProviderError(f"OpenAI generation failed: {exc}")

        try:
            choice = response.choices[0]
            text = choice.message.content
            if text is None:
                raise ProviderError("OpenAI returned an empty response.")

            finish_reason = getattr(choice, "finish_reason", None)
            usage = getattr(response, "usage", None)
            input_tokens = usage.input_tokens if usage else None
            output_tokens = usage.output_tokens if usage else None

            return GenerationResult(
                text=text.strip(),
                provider_name="openai",
                model=self._model,
                finish_reason=finish_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        except (IndexError, AttributeError) as exc:
            raise ProviderError(
                f"Unexpected OpenAI response format: {exc}"
            )

    def name(self) -> str:
        return f"openai/{self._model}"