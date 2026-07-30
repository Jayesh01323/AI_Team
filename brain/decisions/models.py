"""
Data models for the Decision Engine.

These models extend and complement the base ``brain.knowledge`` Decision model
by adding versioning, linking, lifecycle tracking, conflict reporting, and
immutable audit history.

No LLM calls. No persistence. No planning logic.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from brain.knowledge import ConfidenceScore, KnowledgeSource

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _generate_id(prefix: str = "") -> str:
    """Generate a unique identifier with an optional prefix."""
    uid = str(uuid4())
    return f"{prefix}-{uid}" if prefix else uid


# ---------------------------------------------------------------------------
# Extended status enum
# ---------------------------------------------------------------------------


class DecisionStatus(str, Enum):
    """
    Lifecycle status of a decision managed by the Decision Engine.

    Extends the base ``brain.knowledge.DecisionStatus`` to include
    ``proposed`` and ``superseded``, which are needed for the full
    decision lifecycle.
    """

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


# ---------------------------------------------------------------------------
# Conflict models
# ---------------------------------------------------------------------------


class ConflictSeverity(str, Enum):
    """Severity of a detected conflict."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConflictType(str, Enum):
    """The kind of conflict detected."""

    DUPLICATE_ID = "duplicate_id"
    TOPIC_CONFLICT = "topic_conflict"
    CATEGORY_CONFLICT = "category_conflict"
    TECHNOLOGY_CONFLICT = "technology_conflict"
    ARCHITECTURE_CONFLICT = "architecture_conflict"
    CONSTRAINT_VIOLATION = "constraint_violation"


class ConflictReport(BaseModel):
    """
    Structured report of a detected conflict between decisions.

    Returned by :func:`~brain.decisions.conflict_detector.detect_conflicts`
    without modifying any data.
    """

    model_config = ConfigDict(use_enum_values=True)

    conflict_type: ConflictType = Field(..., description="The kind of conflict detected.")
    existing_decision_id: str | None = Field(
        default=None,
        description="ID of the existing decision that is in conflict.",
    )
    new_decision_id: str | None = Field(
        default=None,
        description="ID of the candidate decision being validated.",
    )
    description: str = Field(..., description="Human-readable conflict description.")
    severity: ConflictSeverity = Field(
        default=ConflictSeverity.MEDIUM,
        description="How serious the conflict is.",
    )


# ---------------------------------------------------------------------------
# Validation models
# ---------------------------------------------------------------------------


class ValidationResult(BaseModel):
    """
    Result of validating a decision payload.

    ``is_valid`` is ``True`` only when ``errors`` is empty.
    """

    is_valid: bool = Field(default=True, description="Whether the decision passed all checks.")
    errors: list[str] = Field(default_factory=list, description="List of validation error messages.")

    def add_error(self, message: str) -> None:
        """Append an error and mark result as invalid."""
        self.errors.append(message)
        self.is_valid = False


# ---------------------------------------------------------------------------
# Revision (immutable audit entry)
# ---------------------------------------------------------------------------


class Revision(BaseModel):
    """
    A single immutable entry in a decision's revision history.

    Each time a decision changes, a Revision is appended to its log.
    Revisions are never deleted or modified.
    """

    model_config = ConfigDict(frozen=True, use_enum_values=True)

    version: int = Field(..., ge=1, description="Monotonically increasing revision number.")
    timestamp: str = Field(default_factory=_utc_now_iso, description="When this revision was made.")
    author: str = Field(default="system", description="Who made this change.")
    previous_value: dict[str, Any] | None = Field(
        default=None,
        description="Snapshot of the decision state before the change.",
    )
    new_value: dict[str, Any] = Field(..., description="Snapshot of the decision state after the change.")
    reason: str = Field(default="", description="Why this change was made.")
    action: str = Field(
        default="update",
        description="What action was performed: create, update, accept, reject, supersede.",
    )


# ---------------------------------------------------------------------------
# DecisionRecord (the core managed entity)
# ---------------------------------------------------------------------------


class DecisionRecord(BaseModel):
    """
    A fully managed decision tracked by the Decision Engine.

    Extends the base ``brain.knowledge.Decision`` structure with:
    - Explicit title and category fields (required by the engine)
    - Version tracking
    - Links to requirements, constraints, assumptions, and open questions
    - Supersession references
    - Confidence as a numeric score (0.0–1.0)
    """

    model_config = ConfigDict(use_enum_values=True)

    # Identity
    id: str = Field(default_factory=lambda: _generate_id("dec"), description="Unique decision ID.")
    title: str = Field(..., min_length=1, description="Short, human-readable title.")
    topic: str = Field(..., min_length=1, description="What this decision is about.")
    category: str = Field(..., min_length=1, description="Decision category (e.g. architecture, technology, security).")

    # Content
    value: str = Field(..., min_length=1, description="The chosen decision value.")
    rationale: str = Field(..., min_length=1, description="Why this value was chosen.")
    alternatives: list[str] = Field(
        default_factory=list,
        description="Other options considered and rejected.",
    )

    # Lifecycle
    status: DecisionStatus = Field(
        default=DecisionStatus.PROPOSED,
        description="Current lifecycle status.",
    )
    version: int = Field(default=1, ge=1, description="Current version number (increments on each update).")
    timestamp: str = Field(default_factory=_utc_now_iso, description="When this decision was first created.")
    updated_at: str = Field(default_factory=_utc_now_iso, description="When this decision was last modified.")

    # Confidence
    confidence: ConfidenceScore = Field(
        default_factory=ConfidenceScore,
        description="Confidence in this decision.",
    )

    # Provenance
    source: KnowledgeSource = Field(
        default=KnowledgeSource.USER,
        description="Where this decision originated.",
    )
    author: str = Field(default="system", description="Who created or last modified this decision.")

    # Links to other knowledge artifacts
    linked_requirements: list[str] = Field(
        default_factory=list,
        description="IDs of requirements this decision relates to.",
    )
    linked_constraints: list[str] = Field(
        default_factory=list,
        description="IDs of constraints this decision relates to.",
    )
    linked_assumptions: list[str] = Field(
        default_factory=list,
        description="IDs of assumptions this decision relates to.",
    )
    linked_questions: list[str] = Field(
        default_factory=list,
        description="IDs of open questions this decision answers or relates to.",
    )

    # Supersession chain
    supersedes: str | None = Field(
        default=None,
        description="ID of the decision this one replaces.",
    )
    superseded_by: str | None = Field(
        default=None,
        description="ID of the decision that replaced this one.",
    )

    # Rejection info
    rejection_reason: str | None = Field(default=None, description="Why the decision was rejected.")

    @field_validator("confidence", mode="before")
    @classmethod
    def coerce_confidence(cls, v: Any) -> Any:
        """Allow passing a plain float as a confidence score."""
        if isinstance(v, (int, float)):
            from brain.knowledge import ConfidenceLevel

            level = ConfidenceLevel.UNKNOWN
            if v >= 0.9:
                level = ConfidenceLevel.CERTAIN
            elif v >= 0.7:
                level = ConfidenceLevel.HIGH
            elif v >= 0.5:
                level = ConfidenceLevel.MEDIUM
            elif v > 0.0:
                level = ConfidenceLevel.LOW
            return ConfidenceScore(score=float(v), level=level)
        return v

    def to_snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot of the decision state."""
        return self.model_dump()


# ---------------------------------------------------------------------------
# Engine state (in-memory store, no persistence)
# ---------------------------------------------------------------------------


class DecisionEngineState(BaseModel):
    """
    In-memory store for the Decision Engine.

    Holds all managed decisions and their immutable revision histories.
    This model is intentionally NOT persisted — it exists only for the
    duration of the engine's lifetime.
    """

    decisions: dict[str, DecisionRecord] = Field(
        default_factory=dict,
        description="All decisions keyed by their ID.",
    )
    history: dict[str, list[Revision]] = Field(
        default_factory=dict,
        description="Revision histories keyed by decision ID.",
    )
