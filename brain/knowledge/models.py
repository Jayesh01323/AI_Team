"""
Pydantic models for the Product Knowledge Model.

These models represent WHAT the system knows about a software project.
They do NOT contain logic for HOW knowledge is extracted or generated.

All models use Pydantic v2 for validation, serialization, and type safety.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _generate_id(prefix: str = "") -> str:
    """Generate a unique identifier with an optional prefix."""
    uid = str(uuid4())
    return f"{prefix}-{uid}" if prefix else uid


# ---------------------------------------------------------------------------
# Foundational models
# ---------------------------------------------------------------------------


class ConfidenceScore(BaseModel):
    """
    Represents the confidence level associated with a piece of knowledge.

    Combines a qualitative level with an optional numeric score (0.0–1.0)
    and the source from which the confidence was derived.
    """

    model_config = ConfigDict(use_enum_values=True)

    level: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN,
        description="Qualitative confidence level.",
    )
    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional numeric confidence score between 0.0 and 1.0.",
    )
    source: KnowledgeSource = Field(
        default=KnowledgeSource.AI_INFERENCE,
        description="Where this confidence assessment originated.",
    )
    reasoning: str | None = Field(
        default=None,
        description="Optional explanation for why this confidence was assigned.",
    )

    @field_validator("score")
    @classmethod
    def validate_score_range(cls, v: float | None) -> float | None:
        """Ensure the numeric score, if provided, is within [0.0, 1.0]."""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0.")
        return v


class ProjectMetadata(BaseModel):
    """
    Metadata about the project knowledge artifact itself.

    Tracks version, creation time, last update, and the current
    project lifecycle state.
    """

    model_config = ConfigDict(use_enum_values=True)

    project_id: str = Field(default_factory=lambda: _generate_id("project"))
    project_name: str = Field(default="", description="Human-readable project name.")
    version: str = Field(default="0.1.0", description="Semantic version of the knowledge model.")
    created_at: str = Field(default_factory=_utc_now_iso)
    updated_at: str = Field(default_factory=_utc_now_iso)
    state: ProjectState = Field(
        default=ProjectState.INITIALIZATION,
        description="Current lifecycle state of the project.",
    )
    tags: list[str] = Field(default_factory=list, description="Free-form tags for categorization.")


# ---------------------------------------------------------------------------
# Decision model
# ---------------------------------------------------------------------------


class Decision(BaseModel):
    """
    A single decision made about the project.

    Captures the topic, chosen value, rationale, alternatives considered,
    confidence, source, and lifecycle status.
    """

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: _generate_id("decision"))
    topic: str = Field(..., min_length=1, description="What this decision is about.")
    value: str = Field(..., min_length=1, description="The chosen decision value.")
    rationale: str = Field(default="", description="Why this value was chosen.")
    alternatives: list[str] = Field(
        default_factory=list,
        description="Other options that were considered and rejected.",
    )
    confidence: ConfidenceScore = Field(
        default_factory=ConfidenceScore,
        description="Confidence in this decision.",
    )
    source: KnowledgeSource = Field(
        default=KnowledgeSource.AI_INFERENCE,
        description="Where this decision originated.",
    )
    timestamp: str = Field(default_factory=_utc_now_iso)
    status: DecisionStatus = Field(
        default=DecisionStatus.PENDING,
        description="Lifecycle status of this decision.",
    )


# ---------------------------------------------------------------------------
# Requirement model
# ---------------------------------------------------------------------------


class Requirement(BaseModel):
    """
    A single functional or non-functional requirement.

    Supports priority, status, dependencies, and provenance tracking.
    """

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: _generate_id("req"))
    title: str = Field(..., min_length=1, description="Short title of the requirement.")
    description: str = Field(default="", description="Detailed description.")
    priority: RequirementPriority = Field(
        default=RequirementPriority.MEDIUM,
        description="Priority level of this requirement.",
    )
    status: RequirementStatus = Field(
        default=RequirementStatus.PROPOSED,
        description="Lifecycle status of this requirement.",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="IDs of other requirements this one depends on.",
    )
    source: KnowledgeSource = Field(
        default=KnowledgeSource.USER,
        description="Where this requirement originated.",
    )
    confidence: ConfidenceScore = Field(
        default_factory=ConfidenceScore,
        description="Confidence in this requirement.",
    )


# ---------------------------------------------------------------------------
# Constraint model
# ---------------------------------------------------------------------------


class Constraint(BaseModel):
    """
    A constraint that the project must operate within.

    Examples: budget limits, preferred language, deployment limitations,
    time constraints, compliance requirements.
    """

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: _generate_id("constraint"))
    type: ConstraintType = Field(
        default=ConstraintType.OTHER,
        description="Category of this constraint.",
    )
    name: str = Field(..., min_length=1, description="Short name of the constraint.")
    description: str = Field(default="", description="Detailed description.")
    value: str | None = Field(default=None, description="The constraint value or limit.")
    source: KnowledgeSource = Field(
        default=KnowledgeSource.USER,
        description="Where this constraint originated.",
    )
    confidence: ConfidenceScore = Field(
        default_factory=ConfidenceScore,
        description="Confidence in this constraint.",
    )


# ---------------------------------------------------------------------------
# Assumption model
# ---------------------------------------------------------------------------


class Assumption(BaseModel):
    """
    An assumption made about the project context.

    Assumptions are things we believe to be true but have not verified.
    """

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: _generate_id("assumption"))
    statement: str = Field(..., min_length=1, description="The assumption being made.")
    rationale: str = Field(default="", description="Why this assumption was made.")
    confidence: ConfidenceScore = Field(
        default_factory=ConfidenceScore,
        description="Confidence in this assumption.",
    )
    source: KnowledgeSource = Field(
        default=KnowledgeSource.AI_INFERENCE,
        description="Where this assumption originated.",
    )
    validated: bool = Field(default=False, description="Whether this assumption has been verified.")


# ---------------------------------------------------------------------------
# Open Question model
# ---------------------------------------------------------------------------


class OpenQuestion(BaseModel):
    """
    An open question that needs to be answered before proceeding.

    Questions can be blocking (must be answered before the next stage)
    or non-blocking (can be answered in parallel).
    """

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: _generate_id("question"))
    question: str = Field(..., min_length=1, description="The question to be answered.")
    importance: QuestionImportance = Field(
        default=QuestionImportance.MEDIUM,
        description="How important this question is.",
    )
    reason: str = Field(default="", description="Why this question needs to be asked.")
    blocking: bool = Field(
        default=False,
        description="Whether this question blocks further progress.",
    )
    status: str = Field(
        default="open",
        description="Status of the question: open, answered, dismissed.",
    )
    answer: str | None = Field(default=None, description="The answer, if resolved.")
    answered_at: str | None = Field(
        default=None,
        description="Timestamp when the question was answered.",
    )


# ---------------------------------------------------------------------------
# User Preference model
# ---------------------------------------------------------------------------


class UserPreference(BaseModel):
    """
    A user preference stored as key-value pairs.

    This model is intentionally generic and extensible. Any preference
    (language, framework, cloud, coding style, deployment) can be stored
    using the ``category`` and ``key`` fields.

    Example::

        UserPreference(category="language", key="backend", value="python")
        UserPreference(category="cloud", key="provider", value="aws")
    """

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: _generate_id("pref"))
    category: str = Field(
        ...,
        min_length=1,
        description="Preference category (e.g. 'language', 'framework', 'cloud').",
    )
    key: str = Field(
        ...,
        min_length=1,
        description="Specific preference key (e.g. 'backend', 'provider').",
    )
    value: str = Field(..., min_length=1, description="The preferred value.")
    confidence: ConfidenceScore = Field(
        default_factory=ConfidenceScore,
        description="Confidence in this preference.",
    )
    source: KnowledgeSource = Field(
        default=KnowledgeSource.USER,
        description="Where this preference originated.",
    )
    notes: str | None = Field(default=None, description="Optional additional context.")


# ---------------------------------------------------------------------------
# Aggregate root: ProjectKnowledge
# ---------------------------------------------------------------------------


class ProjectKnowledge(BaseModel):
    """
    The aggregate root of the Product Knowledge Model.

    This is the single source of truth that every future Milestone 4
    component (Intent Engine, Decision Engine, Planning Engine, etc.)
    reads from and writes to.

    The model is designed for progressive enrichment — sections start
    empty and are populated as the system learns more about the project.
    """

    model_config = ConfigDict(use_enum_values=True)

    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)

    # Vision and problem
    vision: str = Field(default="", description="The project vision statement.")
    problem: str = Field(default="", description="The problem the project solves.")
    target_users: list[str] = Field(
        default_factory=list,
        description="Target user segments.",
    )
    business_goals: list[str] = Field(
        default_factory=list,
        description="Business objectives the project aims to achieve.",
    )

    # Requirements
    functional_requirements: list[Requirement] = Field(default_factory=list)
    non_functional_requirements: list[Requirement] = Field(default_factory=list)

    # Knowledge artifacts
    decisions: list[Decision] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    user_preferences: list[UserPreference] = Field(default_factory=list)

    # Notes (free-form, for future growth)
    architecture_notes: list[str] = Field(default_factory=list)
    deployment_notes: list[str] = Field(default_factory=list)
    testing_notes: list[str] = Field(default_factory=list)

    # Extensibility: arbitrary additional data
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional unstructured knowledge for future extensions.",
    )

    def touch(self) -> None:
        """Update the ``updated_at`` timestamp to the current time."""
        self.metadata.updated_at = _utc_now_iso()