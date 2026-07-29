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


def extract_json_from_response(text: str) -> dict[str, Any]:
    """Extract a JSON object from an LLM response string.

    Handles:
    - Raw JSON strings
    - JSON wrapped in markdown code fences (```json ... ```)
    - JSON embedded in surrounding text (regex fallback)

    Args:
        text: The raw LLM response text.

    Returns:
        Parsed JSON as a dictionary.

    Raises:
        ProviderError: If no valid JSON can be extracted.
    """
    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Attempt direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Regex fallback: find the outermost { ... }
    logger.warning("Failed to parse JSON directly, trying regex fallback")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ProviderError(f"Provider returned invalid JSON: {text[:200]}")
