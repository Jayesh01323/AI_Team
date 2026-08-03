"""
Unit tests for AutoProvider, provider selection, failover logic, and configuration.
"""

from unittest.mock import MagicMock
import pytest

from core.exceptions import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
)
from models.common import GenerationResult
from providers.auto import AutoProvider
from providers.base import AIProvider
from providers.factory import create_provider
from providers.gemini import GeminiProvider
from providers.nvidia import NvidiaProvider


class MockProvider(AIProvider):
    def __init__(self, provider_name: str, side_effect=None, return_text: str = "OK"):
        self._provider_name = provider_name
        self.side_effect = side_effect
        self.return_text = return_text
        self.call_count = 0

    def generate(self, prompt: str, max_tokens: int | None = None) -> GenerationResult:
        self.call_count += 1
        if self.side_effect:
            if isinstance(self.side_effect, Exception):
                raise self.side_effect
            raise self.side_effect()
        return GenerationResult(
            text=self.return_text,
            provider_name=self._provider_name,
            model=f"{self._provider_name}-model",
            finish_reason="STOP",
            input_tokens=10,
            output_tokens=5,
        )

    def name(self) -> str:
        return self._provider_name


def test_factory_gemini_selection(monkeypatch):
    """Verify factory returns GeminiProvider when AI_PROVIDER=gemini."""
    monkeypatch.setattr("providers.factory.AI_PROVIDER", "gemini")
    provider = create_provider()
    assert isinstance(provider, GeminiProvider)


def test_factory_nvidia_selection(monkeypatch):
    """Verify factory returns NvidiaProvider when AI_PROVIDER=nvidia."""
    monkeypatch.setattr("providers.factory.AI_PROVIDER", "nvidia")
    provider = create_provider()
    assert isinstance(provider, NvidiaProvider)


def test_factory_auto_selection(monkeypatch):
    """Verify factory returns AutoProvider when AI_PROVIDER=auto."""
    monkeypatch.setattr("providers.factory.AI_PROVIDER", "auto")
    provider = create_provider()
    assert isinstance(provider, AutoProvider)


def test_auto_mode_primary_success():
    """Auto mode succeeds on primary provider if no error occurs."""
    primary = MockProvider("gemini", return_text="Primary Success")
    secondary = MockProvider("nvidia", return_text="Secondary Success")
    auto = AutoProvider(primary=primary, secondary=secondary)

    res = auto.generate("Test prompt")
    assert res.text == "Primary Success"
    assert primary.call_count == 1
    assert secondary.call_count == 0


def test_auto_mode_failover_on_rate_limit():
    """Auto mode fails over to secondary provider on rate limit error."""
    primary = MockProvider("gemini", side_effect=ProviderRateLimitError("Rate limit 429"))
    secondary = MockProvider("nvidia", return_text="Secondary Failover Success")
    auto = AutoProvider(primary=primary, secondary=secondary)

    res = auto.generate("Test prompt")
    assert res.text == "Secondary Failover Success"
    assert primary.call_count == 1
    assert secondary.call_count == 1


def test_auto_mode_failover_on_transient_error():
    """Auto mode fails over to secondary on transient service unavailable error."""
    primary = MockProvider("gemini", side_effect=ProviderError("503 Service Unavailable"))
    secondary = MockProvider("nvidia", return_text="Secondary Failover Success")
    auto = AutoProvider(primary=primary, secondary=secondary)

    res = auto.generate("Test prompt")
    assert res.text == "Secondary Failover Success"
    assert primary.call_count == 1
    assert secondary.call_count == 1


def test_auto_mode_no_failover_on_auth_error():
    """Auto mode does NOT fail over on authentication errors."""
    primary = MockProvider("gemini", side_effect=ProviderAuthenticationError("Invalid Key"))
    secondary = MockProvider("nvidia", return_text="Secondary")
    auto = AutoProvider(primary=primary, secondary=secondary)

    with pytest.raises(ProviderAuthenticationError, match="Invalid Key"):
        auto.generate("Test prompt")

    assert primary.call_count == 1
    assert secondary.call_count == 0


def test_auto_mode_both_providers_fail():
    """Auto mode raises ProviderError when both primary and secondary providers fail."""
    primary = MockProvider("gemini", side_effect=ProviderRateLimitError("Gemini 429"))
    secondary = MockProvider("nvidia", side_effect=ProviderError("NVIDIA error"))
    auto = AutoProvider(primary=primary, secondary=secondary)

    with pytest.raises(ProviderError, match="Auto mode failover failed"):
        auto.generate("Test prompt")

    assert primary.call_count == 1
    assert secondary.call_count == 1


def test_auto_mode_missing_keys_validation(monkeypatch):
    """Verify validation raises issue when neither key is set in auto mode."""
    import core.config as config
    monkeypatch.setattr(config, "AI_PROVIDER", "auto")
    monkeypatch.setattr(config, "GEMINI_API_KEY", None)
    monkeypatch.setattr(config, "NVIDIA_API_KEY", None)

    issues = config.validate()
    assert any("Neither GEMINI_API_KEY nor NVIDIA_API_KEY" in issue for issue in issues)
