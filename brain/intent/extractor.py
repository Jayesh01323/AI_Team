"""
Fact extraction for the Intent Engine.

Extracts only information explicitly supported by the conversation.
No inference, no guessing, no hallucination.
"""

from __future__ import annotations

from typing import Any

from brain.intent.models import ExtractedFact, ConfidenceScore
from brain.intent.rules import (
    BUSINESS_GOAL_INDICATORS,
    BUSINESS_MODEL_RULES,
    CONSTRAINT_RULES,
    PREFERENCE_RULES,
    PROBLEM_INDICATORS,
    PROJECT_TYPE_RULES,
    TARGET_USER_INDICATORS,
    classify_by_rules,
    get_matched_keywords,
    is_explicit_statement,
    match_keywords,
)


def normalize_text(text: str) -> str:
    """
    Normalize text for deterministic matching.

    Args:
        text: Raw input text.

    Returns:
        Lowercased, stripped text.
    """
    return text.strip().lower()


def extract_project_type(text: str) -> ExtractedFact | None:
    """
    Extract project type from text.

    Args:
        text: Input text.

    Returns:
        ExtractedFact if a project type is found, None otherwise.
    """
    normalized = normalize_text(text)
    category, confidence, keywords = classify_by_rules(normalized, PROJECT_TYPE_RULES)
    if category:
        return ExtractedFact(
            category="project_type",
            value=category,
            source_text=text,
            confidence=_make_confidence(confidence, is_explicit_statement(text)),
        )
    return None


def extract_domain(text: str) -> ExtractedFact | None:
    """
    Extract domain from text.

    Args:
        text: Input text.

    Returns:
        ExtractedFact if a domain is found, None otherwise.
    """
    normalized = normalize_text(text)
    category, confidence, keywords = classify_by_rules(normalized, {
        "ai": [],  # placeholder, will use DOMAIN_RULES from rules module
    })
    # Use DOMAIN_RULES directly
    from brain.intent.rules import DOMAIN_RULES
    category, confidence, keywords = classify_by_rules(normalized, DOMAIN_RULES)
    if category:
        return ExtractedFact(
            category="domain",
            value=category,
            source_text=text,
            confidence=_make_confidence(confidence, is_explicit_statement(text)),
        )
    return None


def extract_product_category(text: str) -> ExtractedFact | None:
    """
    Extract product category from text.

    Args:
        text: Input text.

    Returns:
        ExtractedFact if a product category is found, None otherwise.
    """
    normalized = normalize_text(text)
    from brain.intent.rules import PRODUCT_CATEGORY_RULES
    category, confidence, keywords = classify_by_rules(normalized, PRODUCT_CATEGORY_RULES)
    if category:
        return ExtractedFact(
            category="product_category",
            value=category,
            source_text=text,
            confidence=_make_confidence(confidence, is_explicit_statement(text)),
        )
    return None


def extract_business_model(text: str) -> ExtractedFact | None:
    """
    Extract business model from text.

    Args:
        text: Input text.

    Returns:
        ExtractedFact if a business model is found, None otherwise.
    """
    normalized = normalize_text(text)
    category, confidence, keywords = classify_by_rules(normalized, BUSINESS_MODEL_RULES)
    if category:
        return ExtractedFact(
            category="business_model",
            value=category,
            source_text=text,
            confidence=_make_confidence(confidence, is_explicit_statement(text)),
        )
    return None


def extract_constraints(text: str) -> list[ExtractedFact]:
    """
    Extract constraints from text.

    Args:
        text: Input text.

    Returns:
        List of ExtractedFact for each constraint found.
    """
    facts: list[ExtractedFact] = []
    normalized = normalize_text(text)

    for constraint_type, (keywords, _) in CONSTRAINT_RULES.items():
        matched = get_matched_keywords(normalized, keywords)
        if matched:
            # Use the first matched keyword as the constraint value
            value = matched[0]
            facts.append(
                ExtractedFact(
                    category="constraint",
                    value=value,
                    source_text=text,
                    confidence=_make_confidence(0.85, is_explicit_statement(text)),
                )
            )

    return facts


def extract_preferences(text: str) -> list[ExtractedFact]:
    """
    Extract preferences from text.

    Args:
        text: Input text.

    Returns:
        List of ExtractedFact for each preference found.
    """
    facts: list[ExtractedFact] = []
    normalized = normalize_text(text)

    for pref_category, keywords in PREFERENCE_RULES.items():
        matched = get_matched_keywords(normalized, keywords)
        if matched:
            value = matched[0]
            facts.append(
                ExtractedFact(
                    category="preference",
                    value=value,
                    source_text=text,
                    confidence=_make_confidence(0.85, is_explicit_statement(text)),
                )
            )

    return facts


def extract_target_users(text: str) -> ExtractedFact | None:
    """
    Extract target users from text.

    Args:
        text: Input text.

    Returns:
        ExtractedFact if target users are found, None otherwise.
    """
    if match_keywords(text, TARGET_USER_INDICATORS):
        # Look for patterns like "for developers", "for students", etc.
        normalized = normalize_text(text)
        # Simple extraction: look for "for <something>" patterns
        import re
        matches = re.findall(r"for\s+(\w+)", normalized)
        if matches:
            return ExtractedFact(
                category="target_user",
                value=matches[0],
                source_text=text,
                confidence=_make_confidence(0.8, is_explicit_statement(text)),
            )
    return None


def extract_business_goals(text: str) -> ExtractedFact | None:
    """
    Extract business goals from text.

    Args:
        text: Input text.

    Returns:
        ExtractedFact if a business goal is found, None otherwise.
    """
    if match_keywords(text, BUSINESS_GOAL_INDICATORS):
        normalized = normalize_text(text)
        # Look for patterns like "increase revenue", "reduce costs", etc.
        import re
        matches = re.findall(r"(increase|decrease|reduce|improve|optimize)\s+(\w+)", normalized)
        if matches:
            verb, noun = matches[0]
            return ExtractedFact(
                category="business_goal",
                value=f"{verb} {noun}",
                source_text=text,
                confidence=_make_confidence(0.8, is_explicit_statement(text)),
            )
    return None


def extract_problem(text: str) -> ExtractedFact | None:
    """
    Extract problem statement from text.

    Args:
        text: Input text.

    Returns:
        ExtractedFact if a problem is found, None otherwise.
    """
    if match_keywords(text, PROBLEM_INDICATORS):
        normalized = normalize_text(text)
        # Look for patterns like "problem is X", "issue with X", etc.
        import re
        patterns = [
            r"problem\s+(?:is|with)\s+(.+?)(?:\.|$)",
            r"issue\s+(?:is|with)\s+(.+?)(?:\.|$)",
            r"pain\s+point\s+(?:is|with)\s+(.+?)(?:\.|$)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, normalized)
            if matches:
                return ExtractedFact(
                    category="problem",
                    value=matches[0].strip(),
                    source_text=text,
                    confidence=_make_confidence(0.85, is_explicit_statement(text)),
                )
    return None


def extract_requirements(text: str) -> list[ExtractedFact]:
    """
    Extract requirements from text.

    Args:
        text: Input text.

    Returns:
        List of ExtractedFact for each requirement found.
    """
    facts: list[ExtractedFact] = []
    normalized = normalize_text(text)

    # Look for requirement indicators
    requirement_indicators = [
        "must", "should", "need to", "require", "necessary",
        "essential", "important", "critical",
    ]

    if match_keywords(text, requirement_indicators):
        # Extract the requirement statement
        import re
        # Look for patterns like "must do X", "should do X", etc.
        matches = re.findall(r"(?:must|should|need to|require)\s+(.+?)(?:\.|$)", normalized)
        for match in matches:
            if len(match.strip()) > 3:  # Avoid very short matches
                facts.append(
                    ExtractedFact(
                        category="requirement",
                        value=match.strip(),
                        source_text=text,
                        confidence=_make_confidence(0.8, is_explicit_statement(text)),
                    )
                )

    return facts


def extract_all_facts(text: str) -> list[ExtractedFact]:
    """
    Extract all facts from text.

    Args:
        text: Input text.

    Returns:
        List of all ExtractedFact found in the text.
    """
    facts: list[ExtractedFact] = []

    # Extract different types of facts
    extractors = [
        extract_project_type,
        extract_domain,
        extract_product_category,
        extract_business_model,
        extract_problem,
        extract_target_users,
        extract_business_goals,
    ]

    for extractor in extractors:
        fact = extractor(text)
        if fact:
            facts.append(fact)

    # Extract lists of facts
    facts.extend(extract_constraints(text))
    facts.extend(extract_preferences(text))
    facts.extend(extract_requirements(text))

    return facts


def _make_confidence(base: float, is_explicit: bool) -> ConfidenceScore:
    """
    Create a ConfidenceScore with appropriate level.

    Args:
        base: Base numeric confidence.
        is_explicit: Whether the statement was explicit.

    Returns:
        ConfidenceScore instance.
    """
    from brain.knowledge import ConfidenceLevel, KnowledgeSource

    if not is_explicit:
        base -= 0.2

    base = max(0.0, min(1.0, base))

    if base >= 0.8:
        level = ConfidenceLevel.HIGH
    elif base >= 0.6:
        level = ConfidenceLevel.MEDIUM
    elif base >= 0.4:
        level = ConfidenceLevel.LOW
    else:
        level = ConfidenceLevel.UNKNOWN

    return ConfidenceScore(
        level=level,
        score=base,
        source=KnowledgeSource.USER,
    )