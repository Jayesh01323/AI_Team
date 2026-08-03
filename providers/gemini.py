"""
Google Gemini provider implementation.

Requires GEMINI_API_KEY environment variable.
Uses Google Generative Language REST API under the hood.
"""

import json
import urllib.error
import urllib.request

from core.config import GEMINI_API_KEY, GEMINI_MODEL
from core.exceptions import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
)
from core.logging import get_logger
from models.common import GenerationResult
from providers.base import AIProvider

logger = get_logger(__name__)


class GeminiProvider(AIProvider):
    """Concrete provider for Google Gemini models."""

    def __init__(self) -> None:
        self._model = GEMINI_MODEL or "gemini-1.5-pro"
        self._api_key = GEMINI_API_KEY

    def generate(self, prompt: str, max_tokens: int | None = None) -> GenerationResult:
        """
        Send a prompt to Google Gemini and return a structured GenerationResult.

        Args:
            prompt: The input prompt string.
            max_tokens: Optional maximum tokens to generate.

        Returns:
            GenerationResult containing generated text and usage metadata.
        """
        if not self._api_key:
            raise ProviderAuthenticationError(
                "GEMINI_API_KEY is not set. Set it in your environment or .env file."
            )

        models_to_try = [self._model]
        fallbacks = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.0-flash"]
        for fb in fallbacks:
            if fb not in models_to_try:
                models_to_try.append(fb)

        result: GenerationResult | None = None
        last_exc: Exception | None = None

        for model_candidate in models_to_try:
            clean_model = model_candidate.removeprefix("models/")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={self._api_key}"

            payload: dict = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if max_tokens:
                payload["generationConfig"] = {"maxOutputTokens": max_tokens}

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}
            )

            logger.debug(
                "Gemini generate: model=%s max_tokens=%s",
                clean_model,
                max_tokens,
            )

            try:
                with urllib.request.urlopen(req) as response:  # nosec B310

                    res_data = json.loads(response.read().decode("utf-8"))

                candidates = res_data.get("candidates", [])
                if not candidates:
                    raise ProviderError("Gemini returned an empty candidates list.")

                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts if "text" in p)
                if not text:
                    raise ProviderError("Gemini returned an empty text response.")

                finish_reason = candidates[0].get("finishReason")
                usage = res_data.get("usageMetadata", {})
                input_tokens = usage.get("promptTokenCount")
                output_tokens = usage.get("candidatesTokenCount")

                result = GenerationResult(
                    text=text.strip(),
                    provider_name="gemini",
                    model=clean_model,
                    finish_reason=finish_reason,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )
                break

            except urllib.error.HTTPError as exc:
                err_body = exc.read().decode("utf-8", errors="replace")
                err_lower = err_body.lower()

                if (
                    exc.code in (401, 403)
                    or "api key" in err_lower
                    or "authentication" in err_lower
                ):
                    raise ProviderAuthenticationError(
                        f"Gemini authentication failed: {err_body}"
                    ) from exc

                if (
                    exc.code == 429
                    or "quota" in err_lower
                    or "rate limit" in err_lower
                ):
                    last_exc = ProviderRateLimitError(
                        f"Gemini rate limit exceeded: {err_body}"
                    )
                    continue

                if exc.code == 404 or "not found" in err_lower:
                    last_exc = ProviderError(
                        f"Gemini model '{clean_model}' not found or deprecated: {err_body}"
                    )
                    continue

                last_exc = ProviderError(f"Gemini generation failed: {err_body}")

            except urllib.error.URLError as exc:
                last_exc = ProviderError(f"Gemini network error: {exc}")

        if result is not None:
            return result

        if last_exc is not None:
            raise last_exc

        raise ProviderError("Gemini generation failed with no response.")

    def name(self) -> str:
        return f"gemini/{self._model}"

