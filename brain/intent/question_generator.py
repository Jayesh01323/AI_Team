"""
Question generation for the Intent Engine.

Generates clarification questions ONLY when required.
Avoids duplicates, avoids asking for known information,
prioritizes blocking questions, and enforces a maximum of 5 questions.
"""

from __future__ import annotations

from brain.intent.models import Gap, OpenQuestion
from brain.intent.rules import MAX_QUESTIONS, MIN_QUESTION_IMPORTANCE
from brain.knowledge import QuestionImportance


def generate_questions(
    gaps: list[Gap],
    known_sections: list[str],
    max_questions: int = MAX_QUESTIONS,
) -> list[OpenQuestion]:
    """
    Generate clarification questions from detected gaps.

    Args:
        gaps: List of detected gaps.
        known_sections: List of section names already populated.
        max_questions: Maximum number of questions to generate.

    Returns:
        List of OpenQuestion objects, prioritized and deduplicated.
    """
    questions: list[OpenQuestion] = []
    seen_questions: set[str] = set()

    # Sort gaps by importance and blocking status
    sorted_gaps = _sort_gaps_by_priority(gaps)

    for gap in sorted_gaps:
        if len(questions) >= max_questions:
            break

        # Skip if section is already known
        if gap.section in known_sections:
            continue

        # Generate question text
        question_text = _generate_question_text(gap)

        # Deduplicate
        if question_text in seen_questions:
            continue
        seen_questions.add(question_text)

        # Determine importance and blocking status
        importance = _map_importance(gap.importance)
        blocking = gap.is_blocking

        questions.append(
            OpenQuestion(
                question=question_text,
                importance=importance,
                reason=gap.description,
                blocking=blocking,
            )
        )

    return questions


def _sort_gaps_by_priority(gaps: list[Gap]) -> list[Gap]:
    """
    Sort gaps by priority: blocking first, then by importance.

    Args:
        gaps: List of gaps to sort.

    Returns:
        Sorted list of gaps.
    """
    importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    return sorted(
        gaps,
        key=lambda g: (
            0 if g.is_blocking else 1,
            importance_order.get(g.importance, 2),
        ),
    )


def _generate_question_text(gap: Gap) -> str:
    """
    Generate a human-readable question from a gap.

    Args:
        gap: Gap object.

    Returns:
        Question text.
    """
    section_questions = {
        "vision": "What is the long-term vision for this project?",
        "problem": "What specific problem does this project solve?",
        "target_users": "Who are the target users or customers?",
        "business_goals": "What are the main business goals or success metrics?",
        "functional_requirements": "What are the key functional requirements?",
        "non_functional_requirements": "What are the non-functional requirements (performance, security, scalability)?",
        "constraints": "Are there any constraints (budget, timeline, technology)?",
        "user_preferences": "Do you have any preferences for technology or tools?",
    }

    # Return specific question if available
    if gap.section in section_questions:
        return section_questions[gap.section]

    # Generic question based on gap description
    return f"Please provide more information about: {gap.description}"


def _map_importance(importance: str) -> QuestionImportance:
    """
    Map gap importance to question importance.

    Args:
        importance: Gap importance level.

    Returns:
        Question importance level.
    """
    # Ensure minimum importance
    importance_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    current_level = importance_order.get(importance, 1)

    min_level = importance_order.get(MIN_QUESTION_IMPORTANCE, 1)

    if current_level < min_level:
        return QuestionImportance(MIN_QUESTION_IMPORTANCE)

    return QuestionImportance(importance)
