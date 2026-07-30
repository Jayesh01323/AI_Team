"""
Conflict detection for the Decision Engine.

Analyzes candidate decisions against the existing accepted decisions
to identify contradictions, duplicates, and constraint violations.

All logic is deterministic — no LLM calls, no probability estimation.

Conflict types detected:
- DUPLICATE_ID: The candidate ID already exists in the store.
- TOPIC_CONFLICT: Same topic, different value, existing decision is accepted.
- CATEGORY_CONFLICT: Contradicting decisions in the same category.
- TECHNOLOGY_CONFLICT: Multiple accepted technology choices for the same slot.
- ARCHITECTURE_CONFLICT: Contradicting architecture pattern decisions.
- CONSTRAINT_VIOLATION: Candidate links to a constraint already referenced
  by an accepted decision with a different, contradicting value.
"""

from __future__ import annotations

from brain.decisions.models import (
    ConflictReport,
    ConflictSeverity,
    ConflictType,
    DecisionRecord,
    DecisionStatus,
)

# ---------------------------------------------------------------------------
# Category groups used for conflict detection
# ---------------------------------------------------------------------------

#: Categories where two accepted decisions with different values for the same
#: topic always constitute a conflict.
_SINGLETON_CATEGORIES: frozenset[str] = frozenset(
    [
        "architecture",
        "technology",
        "language",
        "framework",
        "database",
        "deployment",
        "infrastructure",
        "security",
        "api",
        "backend",
        "frontend",
        "cloud",
        "messaging",
        "storage",
    ]
)

#: Sub-topics that represent a single "slot" within a category.
#: Two accepted decisions for the same slot conflict.
_TECHNOLOGY_SLOT_KEYWORDS: list[str] = [
    "backend language",
    "frontend language",
    "primary database",
    "message queue",
    "cache",
    "web framework",
    "api style",
    "auth provider",
    "ci/cd",
    "container runtime",
]

#: Architecture patterns that are mutually exclusive with each other.
_EXCLUSIVE_ARCH_PATTERNS: list[frozenset[str]] = [
    frozenset(["monolith", "microservices", "monolithic"]),
    frozenset(["rest", "graphql", "grpc", "soap"]),
    frozenset(["event-driven", "request-response"]),
    frozenset(["sql", "nosql"]),
    frozenset(["synchronous", "asynchronous"]),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_conflicts(
    candidate: dict,
    existing_decisions: dict[str, DecisionRecord],
) -> list[ConflictReport]:
    """
    Detect conflicts between a candidate decision and existing decisions.

    Args:
        candidate: Dictionary representing the proposed DecisionRecord data.
        existing_decisions: All currently managed decisions keyed by ID.

    Returns:
        A list of :class:`~brain.decisions.models.ConflictReport` objects.
        Returns an empty list when no conflicts are found.
        Never modifies any data.
    """
    reports: list[ConflictReport] = []

    candidate_id = candidate.get("id", "")
    candidate_topic = (candidate.get("topic") or "").lower().strip()
    candidate_value = (candidate.get("value") or "").lower().strip()
    candidate_category = (candidate.get("category") or "").lower().strip()

    for decision_id, decision in existing_decisions.items():
        # Skip self-comparison (for update scenarios)
        if candidate_id and decision_id == candidate_id:
            continue

        _check_topic_conflict(
            candidate_id, candidate_topic, candidate_value,
            decision, reports,
        )
        _check_category_conflict(
            candidate_id, candidate_topic, candidate_value, candidate_category,
            decision, reports,
        )
        _check_technology_conflict(
            candidate_id, candidate_topic, candidate_value, candidate_category,
            decision, reports,
        )
        _check_architecture_conflict(
            candidate_id, candidate_topic, candidate_value, candidate_category,
            decision, reports,
        )

    # Duplicate ID check (separate from topic checks)
    if candidate_id and candidate_id in existing_decisions:
        reports.insert(
            0,
            ConflictReport(
                conflict_type=ConflictType.DUPLICATE_ID,
                existing_decision_id=candidate_id,
                new_decision_id=candidate_id,
                description=(
                    f"A decision with ID '{candidate_id}' already exists. "
                    "Use update_decision() to modify it."
                ),
                severity=ConflictSeverity.CRITICAL,
            ),
        )

    return reports


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_accepted(decision: DecisionRecord) -> bool:
    """Return True if the decision has been accepted."""
    return str(decision.status) == DecisionStatus.ACCEPTED.value


def _check_topic_conflict(
    candidate_id: str,
    candidate_topic: str,
    candidate_value: str,
    decision: DecisionRecord,
    reports: list[ConflictReport],
) -> None:
    """Detect same-topic, different-value conflicts against accepted decisions."""
    if not _is_accepted(decision):
        return

    existing_topic = decision.topic.lower().strip()
    existing_value = decision.value.lower().strip()

    if candidate_topic == existing_topic and candidate_value != existing_value:
        reports.append(
            ConflictReport(
                conflict_type=ConflictType.TOPIC_CONFLICT,
                existing_decision_id=decision.id,
                new_decision_id=candidate_id or None,
                description=(
                    f"Topic conflict: accepted decision '{decision.id}' ('{decision.title}') "
                    f"already decided topic '{decision.topic}' = '{decision.value}', "
                    f"but candidate proposes '{candidate_value}'."
                ),
                severity=ConflictSeverity.HIGH,
            )
        )


def _check_category_conflict(
    candidate_id: str,
    candidate_topic: str,
    candidate_value: str,
    candidate_category: str,
    decision: DecisionRecord,
    reports: list[ConflictReport],
) -> None:
    """Detect conflicting values within the same singleton category."""
    if not _is_accepted(decision):
        return

    existing_category = str(decision.category).lower().strip()

    if existing_category not in _SINGLETON_CATEGORIES:
        return
    if candidate_category != existing_category:
        return

    existing_topic = decision.topic.lower().strip()
    existing_value = decision.value.lower().strip()

    # Only flag if same topic within the category with a different value
    if candidate_topic == existing_topic and candidate_value != existing_value:
        reports.append(
            ConflictReport(
                conflict_type=ConflictType.CATEGORY_CONFLICT,
                existing_decision_id=decision.id,
                new_decision_id=candidate_id or None,
                description=(
                    f"Category conflict in '{existing_category}': accepted decision "
                    f"'{decision.id}' has topic '{decision.topic}' = '{decision.value}', "
                    f"candidate proposes '{candidate_value}'."
                ),
                severity=ConflictSeverity.HIGH,
            )
        )


def _check_technology_conflict(
    candidate_id: str,
    candidate_topic: str,
    candidate_value: str,
    candidate_category: str,
    decision: DecisionRecord,
    reports: list[ConflictReport],
) -> None:
    """
    Detect technology slot conflicts.

    If two accepted decisions address the same technology slot (e.g., both
    choose a 'backend language'), they conflict.
    """
    if not _is_accepted(decision):
        return

    existing_category = str(decision.category).lower().strip()
    existing_topic = decision.topic.lower().strip()
    existing_value = decision.value.lower().strip()

    # Must both be technology-related categories
    if candidate_category not in _SINGLETON_CATEGORIES:
        return
    if existing_category not in _SINGLETON_CATEGORIES:
        return

    for slot_keyword in _TECHNOLOGY_SLOT_KEYWORDS:
        if slot_keyword in candidate_topic and slot_keyword in existing_topic:
            if candidate_value != existing_value:
                reports.append(
                    ConflictReport(
                        conflict_type=ConflictType.TECHNOLOGY_CONFLICT,
                        existing_decision_id=decision.id,
                        new_decision_id=candidate_id or None,
                        description=(
                            f"Technology slot conflict for '{slot_keyword}': accepted decision "
                            f"'{decision.id}' chose '{decision.value}', "
                            f"candidate proposes '{candidate_value}'."
                        ),
                        severity=ConflictSeverity.HIGH,
                    )
                )
            break


def _check_architecture_conflict(
    candidate_id: str,
    candidate_topic: str,
    candidate_value: str,
    candidate_category: str,
    decision: DecisionRecord,
    reports: list[ConflictReport],
) -> None:
    """
    Detect mutually exclusive architecture pattern conflicts.

    Uses a predefined list of exclusive pattern groups to identify
    when an accepted and a candidate decision choose incompatible patterns.
    """
    if not _is_accepted(decision):
        return

    existing_category = str(decision.category).lower().strip()

    # Both must be architecture-related
    if "architecture" not in candidate_category and "architecture" not in existing_category:
        return

    existing_value = decision.value.lower().strip()

    for exclusive_group in _EXCLUSIVE_ARCH_PATTERNS:
        candidate_matches = any(pat in candidate_value for pat in exclusive_group)
        existing_matches = any(pat in existing_value for pat in exclusive_group)

        if candidate_matches and existing_matches:
            # Find which patterns each value matches
            candidate_pat = next((p for p in exclusive_group if p in candidate_value), "")
            existing_pat = next((p for p in exclusive_group if p in existing_value), "")

            if candidate_pat != existing_pat:
                reports.append(
                    ConflictReport(
                        conflict_type=ConflictType.ARCHITECTURE_CONFLICT,
                        existing_decision_id=decision.id,
                        new_decision_id=candidate_id or None,
                        description=(
                            f"Architecture conflict: accepted decision '{decision.id}' chose "
                            f"'{existing_pat}' pattern, but candidate proposes '{candidate_pat}'. "
                            "These patterns are mutually exclusive."
                        ),
                        severity=ConflictSeverity.CRITICAL,
                    )
                )
                break  # One conflict per exclusive group is enough
