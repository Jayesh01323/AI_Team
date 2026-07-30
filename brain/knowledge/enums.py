"""
Enumerations for the Product Knowledge Model.

All status, priority, and confidence values are defined as enums
to prevent string-typed inconsistencies across the system.
"""

from enum import Enum


class DecisionStatus(str, Enum):
    """Lifecycle status of a decision."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


class RequirementPriority(str, Enum):
    """Priority level of a requirement."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementStatus(str, Enum):
    """Lifecycle status of a requirement."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REMOVED = "removed"


class QuestionImportance(str, Enum):
    """Importance level of an open question."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceLevel(str, Enum):
    """Confidence level for a piece of knowledge."""

    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CERTAIN = "certain"


class ProjectState(str, Enum):
    """High-level state of the project in its lifecycle."""

    INITIALIZATION = "initialization"
    DISCOVERY = "discovery"
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"


class ConstraintType(str, Enum):
    """Categorization of constraints."""

    BUDGET = "budget"
    TECHNICAL = "technical"
    TIME = "time"
    COMPLIANCE = "compliance"
    RESOURCE = "resource"
    PREFERENCE = "preference"
    OTHER = "other"


class KnowledgeSource(str, Enum):
    """Where a piece of knowledge originated."""

    USER = "user"
    AI_INFERENCE = "ai_inference"
    SYSTEM_DEFAULT = "system_default"
    EXTERNAL_RESEARCH = "external_research"
    VALIDATION = "validation"