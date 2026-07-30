"""
Confidence calculation for the Intent Engine.

Computes deterministic confidence scores for each knowledge section
based on the amount and quality of extracted information.
"""

from __future__ import annotations

from brain.intent.models import SectionConfidence
from brain.intent.rules import GAP_CONFIDENCE_THRESHOLD, MIN_CONFIDENCE_THRESHOLD


def calculate_section_confidence(
    section_name: str,
    has_content: bool,
    content_quality: float = 0.0,
    explicit_count: int = 0,
    total_indicators: int = 0,
) -> SectionConfidence:
    """
    Calculate confidence for a specific knowledge section.

    Args:
        section_name: Name of the section.
        has_content: Whether the section has any content.
        content_quality: Quality score of the content (0.0-1.0).
        explicit_count: Number of explicit statements found.
        total_indicators: Total number of indicators checked.

    Returns:
        SectionConfidence with calculated score and level.
    """
    from brain.knowledge import ConfidenceLevel

    if not has_content:
        return SectionConfidence(
            section=section_name,
            score=0.0,
            level=ConfidenceLevel.UNKNOWN,
            reasoning="No content provided",
        )

    # Base confidence for having content
    base_score = 0.5

    # Boost for explicit statements
    if total_indicators > 0:
        explicit_ratio = explicit_count / total_indicators
        base_score += explicit_ratio * 0.3

    # Boost for content quality
    base_score += content_quality * 0.2

    # Clamp to valid range
    score = max(0.0, min(1.0, base_score))

    # Determine level
    if score >= 0.8:
        level = ConfidenceLevel.HIGH
        reasoning = f"Strong evidence with {explicit_count} explicit statements"
    elif score >= 0.6:
        level = ConfidenceLevel.MEDIUM
        reasoning = f"Moderate evidence with {explicit_count} explicit statements"
    elif score >= MIN_CONFIDENCE_THRESHOLD:
        level = ConfidenceLevel.LOW
        reasoning = f"Weak evidence with {explicit_count} explicit statements"
    else:
        level = ConfidenceLevel.UNKNOWN
        reasoning = f"Insufficient evidence ({explicit_count} explicit statements)"

    return SectionConfidence(
        section=section_name,
        score=score,
        level=level,
        reasoning=reasoning,
    )


def calculate_overall_confidence(
    section_confidences: list[SectionConfidence],
) -> SectionConfidence:
    """
    Calculate overall confidence from individual section confidences.

    Args:
        section_confidences: List of section confidence scores.

    Returns:
        Overall SectionConfidence.
    """
    from brain.knowledge import ConfidenceLevel

    if not section_confidences:
        return SectionConfidence(
            section="overall_intent",
            score=0.0,
            level=ConfidenceLevel.UNKNOWN,
            reasoning="No sections analyzed",
        )

    # Average all section scores
    total_score = sum(section.score for section in section_confidences)
    avg_score = total_score / len(section_confidences)

    # Count high-confidence sections
    high_confidence_count = sum(
        1 for s in section_confidences if s.level == ConfidenceLevel.HIGH
    )

    # Determine overall level
    if avg_score >= 0.8 and high_confidence_count >= len(section_confidences) * 0.6:
        level = ConfidenceLevel.HIGH
        reasoning = f"Strong overall confidence ({high_confidence_count}/{len(section_confidences)} sections high)"
    elif avg_score >= 0.6:
        level = ConfidenceLevel.MEDIUM
        reasoning = f"Moderate overall confidence (avg score: {avg_score:.2f})"
    elif avg_score >= MIN_CONFIDENCE_THRESHOLD:
        level = ConfidenceLevel.LOW
        reasoning = f"Weak overall confidence (avg score: {avg_score:.2f})"
    else:
        level = ConfidenceLevel.UNKNOWN
        reasoning = f"Insufficient overall confidence (avg score: {avg_score:.2f})"

    return SectionConfidence(
        section="overall_intent",
        score=avg_score,
        level=level,
        reasoning=reasoning,
    )


def is_confident(section: SectionConfidence, threshold: float = GAP_CONFIDENCE_THRESHOLD) -> bool:
    """
    Check if a section has sufficient confidence.

    Args:
        section: SectionConfidence to check.
        threshold: Minimum confidence threshold.

    Returns:
        True if confidence is above threshold, False otherwise.
    """
    return section.score >= threshold