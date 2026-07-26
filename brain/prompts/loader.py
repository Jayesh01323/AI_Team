"""
Prompt template loader.

Loads prompt templates from Markdown files in brain/prompts/.
Templates use Python str.format() syntax for placeholders.
"""

from pathlib import Path
from typing import Optional

from core.logging import get_logger

logger = get_logger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(name: str, **kwargs) -> str:
    """
    Load a prompt template from a Markdown file and format it.

    Args:
        name: Template name without extension (e.g. 'idea_analysis').
        **kwargs: Placeholder values for str.format().

    Returns:
        The formatted prompt string.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    filepath = PROMPTS_DIR / f"{name}.md"

    if not filepath.exists():
        raise FileNotFoundError(
            f"Prompt template not found: {filepath}"
        )

    template = filepath.read_text(encoding="utf-8")

    if kwargs:
        return template.format(**kwargs)

    return template


def list_prompts() -> list[str]:
    """Return a list of available prompt template names."""
    return [
        f.stem
        for f in PROMPTS_DIR.glob("*.md")
    ]