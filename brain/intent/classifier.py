"""
Classification for the Intent Engine.

Classifies project type, domain, and product category using
deterministic keyword matching. No inference, no guessing.
"""

from __future__ import annotations

from brain.intent.models import ClassificationResult
from brain.intent.rules import (
    DOMAIN_RULES,
    PRODUCT_CATEGORY_RULES,
    PROJECT_TYPE_RULES,
    classify_by_rules,
)


def classify_project_type(text: str) -> ClassificationResult | None:
    """
    Classify the project type from text.

    Args:
        text: Input text.

    Returns:
        ClassificationResult if a project type is found, None otherwise.
    """
    category, confidence, keywords = classify_by_rules(text, PROJECT_TYPE_RULES)
    if category:
        return ClassificationResult(
            category="project_type",
            value=category,
            confidence=_make_confidence(confidence),
            matched_keywords=keywords,
        )
    return None


def classify_domain(text: str) -> ClassificationResult | None:
    """
    Classify the domain from text.

    Args:
        text: Input text.

    Returns:
        ClassificationResult if a domain is found, None otherwise.
    """
    category, confidence, keywords = classify_by_rules(text, DOMAIN_RULES)
    if category:
        return ClassificationResult(
            category="domain",
            value=category,
            confidence=_make_confidence(confidence),
            matched_keywords=keywords,
        )
    return None


def classify_product_category(text: str) -> ClassificationResult | None:
    """
    Classify the product category from text.

    Args:
        text: Input text.

    Returns:
        ClassificationResult if a product category is found, None otherwise.
    """
    category, confidence, keywords = classify_by_rules(text, PRODUCT_CATEGORY_RULES)
    if category:
        return ClassificationResult(
            category="product_category",
            value=category,
            confidence=_make_confidence(confidence),
            matched_keywords=keywords,
        )
    return None


def classify_all(text: str) -> list[ClassificationResult]:
    """
    Run all classifiers on the text.

    Args:
        text: Input text.

    Returns:
        List of ClassificationResult for each classification found.
    """
    results: list[ClassificationResult] = []

    classifiers = [
        classify_project_type,
        classify_domain,
        classify_product_category,
    ]

    for classifier in classifiers:
        result = classifier(text)
        if result:
            results.append(result)

    return results


def _make_confidence(score: float):
    """
    Create a ConfidenceScore with appropriate level.

    Args:
        score: Numeric confidence score.

    Returns:
        ConfidenceScore instance.
    """
    from brain.knowledge import ConfidenceLevel, ConfidenceScore, KnowledgeSource

    if score >= 0.8:
        level = ConfidenceLevel.HIGH
    elif score >= 0.6:
        level = ConfidenceLevel.MEDIUM
    elif score >= 0.4:
        level = ConfidenceLevel.LOW
    else:
        level = ConfidenceLevel.UNKNOWN

    return ConfidenceScore(
        level=level,
        score=score,
        source=KnowledgeSource.USER,
    )