"""
NVIDIA NIM provider implementation.

Requires NVIDIA_API_KEY environment variable.
Uses NVIDIA NIM API (OpenAI-compatible REST endpoint) under the hood.
"""

import json
import urllib.error
import urllib.request

from core.config import NVIDIA_API_KEY, NVIDIA_MODEL
from core.exceptions import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
)
from core.logging import get_logger
from models.common import GenerationResult
from providers.base import AIProvider

logger = get_logger(__name__)


class NvidiaProvider(AIProvider):
    """Concrete provider for NVIDIA NIM models."""

    def __init__(self) -> None:
        self._model = NVIDIA_MODEL or "meta/llama-3.1-70b-instruct"
        self._api_key = NVIDIA_API_KEY

    def generate(self, prompt: str, max_tokens: int | None = None) -> GenerationResult:
        """
        Send a prompt to NVIDIA NIM API and return a structured GenerationResult.

        Args:
            prompt: The input prompt string.
            max_tokens: Optional maximum tokens to generate.

        Returns:
            GenerationResult containing generated text and usage metadata.
        """
        if not self._api_key:
            raise ProviderAuthenticationError(
                "NVIDIA_API_KEY is not set. Set it in your environment or .env file."
            )

        models_to_try = [self._model]
        fallbacks = [
            "meta/llama-3.1-70b-instruct",
            "meta/llama3-70b-instruct",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "mistralai/mistral-7b-instruct-v0.2",
        ]
        for fb in fallbacks:
            if fb not in models_to_try:
                models_to_try.append(fb)

        result: GenerationResult | None = None
        last_exc: Exception | None = None

        url = "https://integrate.api.nvidia.com/v1/chat/completions"

        for model_candidate in models_to_try:
            payload: dict = {
                "model": model_candidate,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens

            data = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            }
            req = urllib.request.Request(url, data=data, headers=headers)

            logger.debug(
                "NVIDIA NIM generate: model=%s max_tokens=%s",
                model_candidate,
                max_tokens,
            )

            try:
                with urllib.request.urlopen(req) as response:  # nosec B310

                    res_data = json.loads(response.read().decode("utf-8"))

                choices = res_data.get("choices", [])
                if not choices:
                    raise ProviderError("NVIDIA NIM returned an empty choices list.")

                message = choices[0].get("message", {})
                text = message.get("content", "")
                if text is None or not text.strip():
                    raise ProviderError("NVIDIA NIM returned an empty response.")

                finish_reason = choices[0].get("finish_reason")
                usage = res_data.get("usage", {})
                input_tokens = usage.get("prompt_tokens")
                output_tokens = usage.get("completion_tokens")

                result = GenerationResult(
                    text=text.strip(),
                    provider_name="nvidia",
                    model=model_candidate,
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
                    or "unauthorized" in err_lower
                ):
                    raise ProviderAuthenticationError(
                        f"NVIDIA authentication failed: {err_body}"
                    ) from exc

                if (
                    exc.code == 429
                    or "quota" in err_lower
                    or "rate limit" in err_lower
                    or "too many requests" in err_lower
                ):
                    last_exc = ProviderRateLimitError(
                        f"NVIDIA rate limit exceeded: {err_body}"
                    )
                    continue

                if exc.code == 404 or "not found" in err_lower or "unknown model" in err_lower:
                    last_exc = ProviderError(
                        f"NVIDIA model '{model_candidate}' not found: {err_body}"
                    )
                    continue

                last_exc = ProviderError(f"NVIDIA generation failed ({exc.code}): {err_body}")

            except urllib.error.URLError as exc:
                last_exc = ProviderError(f"NVIDIA network error: {exc}")

        if result is not None:
            return result

        if last_exc is not None:
            raise last_exc

        raise ProviderError("NVIDIA generation failed with no response.")

    def name(self) -> str:
        return f"nvidia/{self._model}"
