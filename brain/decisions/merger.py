"""
Safe merge/replacement operations for the Decision Engine.

Provides functions that apply partial updates to DecisionRecord objects
while enforcing lifecycle rules (e.g., accepted decisions cannot be
silently overwritten).

All merges are non-destructive — the original state is captured before
any changes so it can be recorded in the audit history.
"""

from __future__ import annotations

import copy
from typing import Any

from brain.decisions.models import DecisionRecord, DecisionStatus

# ---------------------------------------------------------------------------
# Merge helpers
# ---------------------------------------------------------------------------

#: Fields that cannot be overwritten by a plain update (only by dedicated ops)
_PROTECTED_FIELDS: frozenset[str] = frozenset(
    ["id", "timestamp", "version", "supersedes", "superseded_by"]
)

#: Fields that are allowed in a partial update
_UPDATABLE_FIELDS: frozenset[str] = frozenset(
    [
        "title",
        "topic",
        "category",
        "value",
        "rationale",
        "alternatives",
        "confidence",
        "source",
        "author",
        "status",
        "linked_requirements",
        "linked_constraints",
        "linked_assumptions",
        "linked_questions",
        "rejection_reason",
    ]
)


def apply_update(
    decision: DecisionRecord,
    updates: dict[str, Any],
) -> tuple[dict[str, Any], DecisionRecord]:
    """
    Apply a partial update to a DecisionRecord and return a new instance.

    Args:
        decision: The existing decision to update.
        updates: A dictionary of fields to change. Protected fields
            (``id``, ``timestamp``, ``version``, ``supersedes``,
            ``superseded_by``) are silently stripped before application.

    Returns:
        A tuple of ``(previous_snapshot, updated_decision)`` where
        ``previous_snapshot`` captures the state before the update.

    Raises:
        ValueError: If the decision is ``accepted`` and the caller attempts
            to change ``status`` directly (use ``reject_decision`` or
            ``supersede_decision`` instead).
    """
    _guard_accepted_status_change(decision, updates)

    # Snapshot state before changes
    previous_snapshot = copy.deepcopy(decision.to_snapshot())

    # Strip protected fields
    clean_updates = {k: v for k, v in updates.items() if k not in _PROTECTED_FIELDS}

    # Build updated data dict
    current_data = decision.model_dump()
    for field, value in clean_updates.items():
        if field in _UPDATABLE_FIELDS:
            current_data[field] = value

    # Increment version
    current_data["version"] = decision.version + 1
    current_data["updated_at"] = _utc_now_iso()

    updated_decision = DecisionRecord(**current_data)
    return previous_snapshot, updated_decision


def apply_rejection(
    decision: DecisionRecord,
    reason: str,
    author: str,
) -> tuple[dict[str, Any], DecisionRecord]:
    """
    Mark a decision as rejected.

    Args:
        decision: The existing decision.
        reason: Why the decision is being rejected.
        author: Who is rejecting it.

    Returns:
        ``(previous_snapshot, rejected_decision)``

    Raises:
        ValueError: If the decision is already rejected or superseded.
    """
    current_status = str(decision.status)
    if current_status in (DecisionStatus.REJECTED.value, DecisionStatus.SUPERSEDED.value):
        raise ValueError(
            f"Cannot reject decision '{decision.id}': "
            f"already in terminal status '{current_status}'."
        )

    previous_snapshot = copy.deepcopy(decision.to_snapshot())

    current_data = decision.model_dump()
    current_data["status"] = DecisionStatus.REJECTED.value
    current_data["rejection_reason"] = reason
    current_data["author"] = author
    current_data["version"] = decision.version + 1
    current_data["updated_at"] = _utc_now_iso()

    rejected_decision = DecisionRecord(**current_data)
    return previous_snapshot, rejected_decision


def apply_supersession(
    old_decision: DecisionRecord,
    new_decision: DecisionRecord,
) -> tuple[dict[str, Any], DecisionRecord]:
    """
    Link the old decision as superseded by the new one.

    Args:
        old_decision: The decision being replaced.
        new_decision: The decision that replaces it.

    Returns:
        ``(previous_snapshot, updated_old_decision)`` where
        ``updated_old_decision`` has status ``superseded`` and
        ``superseded_by`` set to the new decision's ID.
    """
    previous_snapshot = copy.deepcopy(old_decision.to_snapshot())

    old_data = old_decision.model_dump()
    old_data["status"] = DecisionStatus.SUPERSEDED.value
    old_data["superseded_by"] = new_decision.id
    old_data["version"] = old_decision.version + 1
    old_data["updated_at"] = _utc_now_iso()

    updated_old = DecisionRecord(**old_data)
    return previous_snapshot, updated_old


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    from datetime import UTC, datetime
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _guard_accepted_status_change(decision: DecisionRecord, updates: dict[str, Any]) -> None:
    """
    Raise if an update attempts to silently change an accepted decision's status.

    An accepted decision's status may only change through explicit engine
    operations (``reject_decision``, ``supersede_decision``).
    """
    if str(decision.status) != DecisionStatus.ACCEPTED.value:
        return

    new_status = updates.get("status")
    if new_status is None:
        return

    # Allow re-asserting the same status
    if str(new_status) == DecisionStatus.ACCEPTED.value:
        return

    raise ValueError(
        f"Cannot silently overwrite accepted decision '{decision.id}'. "
        "Use reject_decision() or supersede_decision() instead."
    )
