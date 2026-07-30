"""
Decision Engine package.

Implements a deterministic Decision Engine for recording, validating,
versioning, and managing project decisions.

No LLM calls. No persistence. No planning logic. No UI.

Public API::

    from brain.decisions import (
        DecisionEngine,
        DecisionRecord,
        DecisionStatus,
        ConflictReport,
        ConflictType,
        ConflictSeverity,
        ValidationResult,
        Revision,
    )
"""

from brain.decisions.engine import DecisionEngine
from brain.decisions.models import (
    ConflictReport,
    ConflictSeverity,
    ConflictType,
    DecisionEngineState,
    DecisionRecord,
    DecisionStatus,
    Revision,
    ValidationResult,
)

__all__ = [
    "ConflictReport",
    "ConflictSeverity",
    "ConflictType",
    "DecisionEngine",
    "DecisionEngineState",
    "DecisionRecord",
    "DecisionStatus",
    "Revision",
    "ValidationResult",
]
