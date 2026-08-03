"""
Shared JSON extraction utility for LLM response parsing.

All LLM-based stages need to extract JSON from provider responses,
which may be wrapped in markdown code fences or contain extraneous text.
"""

import json
import re
from typing import Any

from core.exceptions import ProviderError
from core.logging import get_logger

logger = get_logger(__name__)


def _clean_json_string(s: str) -> str:
    """Remove trailing commas before closing braces/brackets for JSON compatibility."""
    return re.sub(r",\s*([\}\]])", r"\1", s)


def extract_json_from_response(text: str) -> dict[str, Any]:
    """Extract a JSON object from an LLM response string.

    Handles:
    - Raw JSON strings
    - JSON wrapped in markdown code fences (```json ... ```), including preamble/postamble
    - JSON embedded in surrounding text (regex fallback)
    - Trailing comma cleanup

    Args:
        text: The raw LLM response text.

    Returns:
        Parsed JSON as a dictionary.

    Raises:
        ProviderError: If no valid JSON can be extracted.
    """
    if not text or not text.strip():
        raise ProviderError("Provider returned invalid JSON: empty response.")

    text = text.strip()

    cleaned_candidates: list[str] = []

    # 1. Check for markdown code fences anywhere in text
    fence_match = re.search(
        r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL | re.IGNORECASE
    )
    if fence_match:
        cleaned_candidates.append(fence_match.group(1).strip())

    # 2. Raw text with outer fence markers stripped if present
    raw_text = text
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw_text = "\n".join(lines).strip()
    cleaned_candidates.append(raw_text)

    # 3. Outer regex match of { ... }
    obj_match = re.search(r"\{.*\}", text, re.DOTALL)
    if obj_match:
        cleaned_candidates.append(obj_match.group().strip())

    # Try parsing candidate strings
    for candidate in cleaned_candidates:
        if not candidate:
            continue

        # Direct parse attempt
        try:
            val = json.loads(candidate)
            if isinstance(val, dict):
                return val
        except json.JSONDecodeError:
            pass

        # Parse attempt after cleaning trailing commas
        cleaned = _clean_json_string(candidate)
        try:
            val = json.loads(cleaned)
            if isinstance(val, dict):
                return val
        except json.JSONDecodeError:
            pass

    raise ProviderError(f"Provider returned invalid JSON: {text[:200]}")

