"""
Tests for brain.json_utils — shared JSON extraction from LLM responses.
"""

import pytest

from brain.json_utils import extract_json_from_response
from core.exceptions import ProviderError


def test_extract_raw_json():
    """Valid JSON string is parsed directly."""
    text = '{"key": "value", "count": 42}'
    result = extract_json_from_response(text)
    assert result == {"key": "value", "count": 42}


def test_extract_json_with_markdown_fences():
    """JSON wrapped in ```json ... ``` fences is extracted correctly."""
    text = '```json\n{"title": "My Project", "version": "1.0"}\n```'
    result = extract_json_from_response(text)
    assert result == {"title": "My Project", "version": "1.0"}


def test_extract_json_with_plain_fences():
    """JSON wrapped in ``` ... ``` (no language hint) is extracted correctly."""
    text = '```\n{"items": [1, 2, 3]}\n```'
    result = extract_json_from_response(text)
    assert result == {"items": [1, 2, 3]}


def test_extract_json_regex_fallback():
    """JSON embedded in surrounding text is extracted via regex fallback."""
    text = 'Here is the output:\n{"result": "success"}\nEnd of response.'
    result = extract_json_from_response(text)
    assert result == {"result": "success"}


def test_extract_json_whitespace_padding():
    """Leading/trailing whitespace is stripped before parsing."""
    text = '  \n  {"trimmed": true}  \n  '
    result = extract_json_from_response(text)
    assert result == {"trimmed": True}


def test_extract_json_invalid_raises_provider_error():
    """Completely invalid input raises ProviderError."""
    with pytest.raises(ProviderError, match="Provider returned invalid JSON"):
        extract_json_from_response("This is not JSON at all")


def test_extract_json_empty_raises_provider_error():
    """Empty string raises ProviderError."""
    with pytest.raises(ProviderError, match="Provider returned invalid JSON"):
        extract_json_from_response("")


def test_extract_json_nested_objects():
    """Nested JSON structures are preserved."""
    text = '{"outer": {"inner": {"deep": true}}, "list": [1, 2]}'
    result = extract_json_from_response(text)
    assert result["outer"]["inner"]["deep"] is True
    assert result["list"] == [1, 2]


def test_extract_json_multiline_fenced():
    """Multi-line fenced JSON is handled correctly."""
    text = """```json
{
    "project_title": "SaaS App",
    "epics": [
        {
            "title": "Core",
            "stories": []
        }
    ]
}
```"""
    result = extract_json_from_response(text)
    assert result["project_title"] == "SaaS App"
    assert len(result["epics"]) == 1
