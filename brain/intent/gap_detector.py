"""
Gap detection for the Intent Engine.

Compares current ProjectKnowledge against the schema to identify
missing required sections, incomplete information, and blocking unknowns.
"""

from __future__ import annotations

from brain.intent.models import Gap
from brain.intent.rules import MIN_REQUIRED_SECTIONS
from brain.knowledge import PROJECT_SCHEMA, QuestionImportance, is_complete


def detect_gaps(knowledge_dict: dict) -> list[Gap]:
    """
    Detect gaps in project knowledge.

    Args:
        knowledge_dict: Dictionary representation of ProjectKnowledge.

    Returns:
        List of Gap objects representing missing or incomplete sections.
    """
    gaps: list[Gap] = []

    # Check schema completeness
    completeness = is_complete(knowledge_dict)

    # Required sections that are missing
    for section in PROJECT_SCHEMA:
        if section.required and not completeness.get(section.name, False):
            gaps.append(
                Gap(
                    section=section.name,
                    description=f"Required section '{section.label}' is missing",
                    is_blocking=True,
                    importance=QuestionImportance.CRITICAL,
                )
            )

    # Check for minimum required sections
    required_count = sum(1 for s in PROJECT_SCHEMA if s.required and completeness.get(s.name, False))
    if required_count < MIN_REQUIRED_SECTIONS:
        gaps.append(
            Gap(
                section="general",
                description=f"Only {required_count} of {MIN_REQUIRED_SECTIONS} required sections are populated",
                is_blocking=True,
                importance=QuestionImportance.HIGH,
            )
        )

    # Check for empty but present sections
    for section in PROJECT_SCHEMA:
        if completeness.get(section.name, False) is False:
            # Section exists but is empty
            if section.name in knowledge_dict:
                value = knowledge_dict[section.name]
                if isinstance(value, str) and not value.strip():
                    gaps.append(
                        Gap(
                            section=section.name,
                            description=f"Section '{section.label}' is empty",
                            is_blocking=False,
                            importance=QuestionImportance.MEDIUM,
                        )
                    )
                elif isinstance(value, list) and len(value) == 0:
                    gaps.append(
                        Gap(
                            section=section.name,
                            description=f"Section '{section.label}' has no items",
                            is_blocking=False,
                            importance=QuestionImportance.MEDIUM,
                        )
                    )

    return gaps


def get_blocking_gaps(gaps: list[Gap]) -> list[Gap]:
    """
    Filter gaps to only blocking ones.

    Args:
        gaps: List of all gaps.

    Returns:
        List of blocking gaps only.
    """
    return [gap for gap in gaps if gap.is_blocking]


def get_high_priority_gaps(gaps: list[Gap]) -> list[Gap]:
    """
    Filter gaps to high or critical importance.

    Args:
        gaps: List of all gaps.

    Returns:
        List of high-priority gaps.
    """
    return [gap for gap in gaps if gap.importance in ("high", "critical")]