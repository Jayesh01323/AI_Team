"""
Product Knowledge Model package.

The single source of truth for everything the AI Engineering Team knows
about a software project. This package contains only data models and
schema definitions — no extraction, inference, or decision logic.

Public API::

    from brain.knowledge import (
        ProjectKnowledge,
        Decision,
        Requirement,
        Constraint,
        Assumption,
        OpenQuestion,
        UserPreference,
        ConfidenceScore,
        ProjectMetadata,
        ProjectState,
        PROJECT_SCHEMA,
    )
"""

from brain.knowledge.enums import (
    ConfidenceLevel,
    ConstraintType,
    DecisionStatus,
    KnowledgeSource,
    ProjectState,
    QuestionImportance,
    RequirementPriority,
    RequirementStatus,
)
from brain.knowledge.models import (
    Assumption,
    ConfidenceScore,
    Constraint,
    Decision,
    OpenQuestion,
    ProjectKnowledge,
    ProjectMetadata,
    Requirement,
    UserPreference,
)
from brain.knowledge.schema import (
    PROJECT_SCHEMA,
    SchemaSection,
    get_optional_sections,
    get_required_sections,
    get_section_names,
    is_complete,
)

__all__ = [
    # Enums
    "ConfidenceLevel",
    "ConstraintType",
    "DecisionStatus",
    "KnowledgeSource",
    "ProjectState",
    "QuestionImportance",
    "RequirementPriority",
    "RequirementStatus",
    # Models
    "Assumption",
    "ConfidenceScore",
    "Constraint",
    "Decision",
    "OpenQuestion",
    "ProjectKnowledge",
    "ProjectMetadata",
    "Requirement",
    "UserPreference",
    # Schema
    "PROJECT_SCHEMA",
    "SchemaSection",
    "get_optional_sections",
    "get_required_sections",
    "get_section_names",
    "is_complete",
]