"""
Unit tests for GeminiProvider in providers/gemini.py.
"""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch
import urllib.error

import pytest

from core.exceptions import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
)
from models.common import GenerationResult
from providers.gemini import GeminiProvider


def test_gemini_provider_init_and_name():
    provider = GeminiProvider()
    assert "gemini" in provider.name()


def test_gemini_provider_missing_api_key(monkeypatch):
    provider = GeminiProvider()
    provider._api_key = None
    with pytest.raises(ProviderAuthenticationError, match="GEMINI_API_KEY is not set"):
        provider.generate("Hello")


@patch("urllib.request.urlopen")
def test_gemini_provider_generate_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.read.return_value = json.dumps({
        "candidates": [
            {
                "content": {"parts": [{"text": "Hello world!"}]},
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 5,
            "candidatesTokenCount": 2,
        },
    }).encode("utf-8")
    mock_urlopen.return_value = mock_response

    provider = GeminiProvider()
    result = provider.generate("Test prompt", max_tokens=100)

    assert isinstance(result, GenerationResult)
    assert result.text == "Hello world!"
    assert result.provider_name == "gemini"
    assert result.finish_reason == "STOP"
    assert result.input_tokens == 5
    assert result.output_tokens == 2


@patch("urllib.request.urlopen")
def test_gemini_provider_auth_error(mock_urlopen):
    err = urllib.error.HTTPError(
        url="http://test",
        code=401,
        msg="Unauthorized",
        hdrs={},
        fp=BytesIO(b'{"error": "API key invalid"}'),
    )
    mock_urlopen.side_effect = err

    provider = GeminiProvider()
    with pytest.raises(ProviderAuthenticationError, match="authentication failed"):
        provider.generate("Hello")


@patch("urllib.request.urlopen")
def test_gemini_provider_rate_limit_error(mock_urlopen):
    err = urllib.error.HTTPError(
        url="http://test",
        code=429,
        msg="Too Many Requests",
        hdrs={},
        fp=BytesIO(b'{"error": "Quota exceeded"}'),
    )
    mock_urlopen.side_effect = err

    provider = GeminiProvider()
    with pytest.raises(ProviderRateLimitError, match="rate limit exceeded"):
        provider.generate("Hello")
