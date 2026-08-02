"""
Utility functions for the AI Engineering Team.

Centralizes common operations to ensure consistency across the codebase.
"""

import re


def sanitize_project_name(idea: str, max_length: int = 64) -> str:
    """
    Convert an idea string into a sanitized directory name.

    This function is the SINGLE SOURCE OF TRUTH for project name sanitization.
    All other code should import and use this function instead of duplicating the logic.

    Args:
        idea: The raw idea text to sanitize
        max_length: Maximum length for the sanitized name (default: 64)

    Returns:
        A sanitized project name safe for use as a directory name

    Example:
        >>> sanitize_project_name("Build a SaaS Resume Analyzer!")
        'build-a-saas-resume-analyzer'
    """
    name = idea.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    return name[:max_length]