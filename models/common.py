"""
Shared domain types used across the codebase.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationResult:
    """
    Structured result from an AI provider.

    Instead of returning a raw string, providers return this object
    so callers have access to metadata about the generation.
    """

    text: str
    """The generated text content."""

    provider_name: str
    """Name of the provider that generated this result (e.g. 'openai/gpt-4o')."""

    model: str
    """The specific model used (e.g. 'gpt-4o', 'claude-3-5-sonnet')."""

    finish_reason: str | None = None
    """Why the generation finished (e.g. 'stop', 'length', 'error')."""

    input_tokens: int | None = None
    """Number of input/prompt tokens consumed."""

    output_tokens: int | None = None
    """Number of output/completion tokens generated."""
