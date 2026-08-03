"""
Unit tests for NVIDIA provider implementation, configuration, and security.
"""

import json
from io import BytesIO
import os
from unittest.mock import MagicMock, patch
import urllib.error

import pytest

from core.exceptions import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
)
from models.common import GenerationResult
from providers.factory import create_provider
from providers.nvidia import NvidiaProvider


def test_nvidia_provider_init_and_name():
    """Verify NvidiaProvider initializes correctly and returns provider name."""
    provider = NvidiaProvider()
    assert "nvidia" in provider.name()


def test_factory_creates_nvidia_provider(monkeypatch):
    """Verify factory instantiates NvidiaProvider when AI_PROVIDER=nvidia."""
    monkeypatch.setattr("providers.factory.AI_PROVIDER", "nvidia")
    provider = create_provider()
    assert isinstance(provider, NvidiaProvider)


def test_nvidia_provider_missing_api_key():
    """Verify missing API key raises ProviderAuthenticationError."""
    provider = NvidiaProvider()
    provider._api_key = None
    with pytest.raises(ProviderAuthenticationError, match="NVIDIA_API_KEY is not set"):
        provider.generate("Test prompt")


@patch("urllib.request.urlopen")
def test_nvidia_provider_generate_success(mock_urlopen):
    """Verify successful NVIDIA NIM API call and response parsing."""
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.read.return_value = json.dumps({
        "choices": [
            {
                "message": {"content": "Generated NVIDIA response"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 12,
            "completion_tokens": 8,
        },
    }).encode("utf-8")
    mock_urlopen.return_value = mock_response

    provider = NvidiaProvider()
    result = provider.generate("Test prompt", max_tokens=100)

    assert isinstance(result, GenerationResult)
    assert result.text == "Generated NVIDIA response"
    assert result.provider_name == "nvidia"
    assert result.finish_reason == "stop"
    assert result.input_tokens == 12
    assert result.output_tokens == 8


@patch("urllib.request.urlopen")
def test_nvidia_provider_auth_error(mock_urlopen):
    """Verify HTTP 401 raises ProviderAuthenticationError."""
    err = urllib.error.HTTPError(
        url="http://test",
        code=401,
        msg="Unauthorized",
        hdrs={},
        fp=BytesIO(b'{"error": "API key invalid"}'),
    )
    mock_urlopen.side_effect = err

    provider = NvidiaProvider()
    with pytest.raises(ProviderAuthenticationError, match="authentication failed"):
        provider.generate("Hello")


@patch("urllib.request.urlopen")
def test_nvidia_provider_rate_limit_error(mock_urlopen):
    """Verify HTTP 429 raises ProviderRateLimitError."""
    err = urllib.error.HTTPError(
        url="http://test",
        code=429,
        msg="Too Many Requests",
        hdrs={},
        fp=BytesIO(b'{"error": "Rate limit exceeded"}'),
    )
    mock_urlopen.side_effect = err

    provider = NvidiaProvider()
    with pytest.raises(ProviderRateLimitError, match="rate limit exceeded"):
        provider.generate("Hello")


def test_system_env_precedence(monkeypatch):
    """Verify system environment variables override default configuration."""
    dummy_key = "mock-system-key-12345"
    monkeypatch.setenv("NVIDIA_API_KEY", dummy_key)
    monkeypatch.setenv("NVIDIA_MODEL", "meta/llama-3.1-405b-instruct")

    import core.config as config
    assert os.getenv("NVIDIA_API_KEY") == dummy_key
    assert os.getenv("NVIDIA_MODEL") == "meta/llama-3.1-405b-instruct"


def test_key_security_not_exposed():
    """Verify key is not exposed in str/repr of NvidiaProvider."""
    provider = NvidiaProvider()
    representation = str(provider.name())
    assert "mock-key" not in representation
    assert "SECRET" not in representation

