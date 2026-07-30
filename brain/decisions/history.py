"""
Immutable revision history management for the Decision Engine.

Provides functions to record, retrieve, and inspect the full audit trail
of every decision managed by the engine.

Rules:
- Revisions are append-only — never deleted or modified.
- Each revision records a complete before/after snapshot.
- get_history() returns a defensive copy to prevent external mutation.
"""

from __future__ import annotations

import copy

from brain.decisions.models import DecisionRecord, Revision

# ---------------------------------------------------------------------------
# History operations
# ---------------------------------------------------------------------------


def record_revision(
    history_store: dict[str, list[Revision]],
    decision: DecisionRecord,
    previous_snapshot: dict | None,
    author: str,
    reason: str,
    action: str,
) -> Revision:
    """
    Append a new revision to the immutable history log for a decision.

    Args:
        history_store: The engine's central history dictionary (mutated in place).
        decision: The decision *after* the change has been applied.
        previous_snapshot: The decision state *before* the change, or ``None``
            for initial creation.
        author: Who made this change.
        reason: Why this change was made.
        action: The action performed (``create``, ``update``, ``accept``,
            ``reject``, ``supersede``).

    Returns:
        The newly created :class:`~brain.decisions.models.Revision`.
    """
    decision_id = decision.id
    existing_revisions = history_store.get(decision_id, [])
    next_version = len(existing_revisions) + 1

    revision = Revision(
        version=next_version,
        author=author,
        previous_value=copy.deepcopy(previous_snapshot) if previous_snapshot else None,
        new_value=copy.deepcopy(decision.to_snapshot()),
        reason=reason,
        action=action,
    )

    if decision_id not in history_store:
        history_store[decision_id] = []

    history_store[decision_id].append(revision)
    return revision


def get_history(
    history_store: dict[str, list[Revision]],
    decision_id: str,
) -> list[Revision]:
    """
    Return the complete, ordered revision history for a decision.

    Args:
        history_store: The engine's central history dictionary.
        decision_id: The ID of the decision to look up.

    Returns:
        A defensive copy of the revision list, ordered oldest → newest.
        Returns an empty list if the decision has no recorded history.
    """
    revisions = history_store.get(decision_id, [])
    return copy.deepcopy(revisions)


def get_latest_revision(
    history_store: dict[str, list[Revision]],
    decision_id: str,
) -> Revision | None:
    """
    Return the most recent revision for a decision, or ``None``.

    Args:
        history_store: The engine's central history dictionary.
        decision_id: The ID of the decision to look up.

    Returns:
        The latest :class:`~brain.decisions.models.Revision`, or ``None``
        if no history exists for this ID.
    """
    revisions = history_store.get(decision_id, [])
    if not revisions:
        return None
    return copy.deepcopy(revisions[-1])


def revision_count(
    history_store: dict[str, list[Revision]],
    decision_id: str,
) -> int:
    """
    Return the number of revisions recorded for a decision.

    Args:
        history_store: The engine's central history dictionary.
        decision_id: The ID of the decision to look up.

    Returns:
        Integer count of revisions (0 if none).
    """
    return len(history_store.get(decision_id, []))


def list_all_authors(
    history_store: dict[str, list[Revision]],
    decision_id: str,
) -> list[str]:
    """
    Return the distinct list of authors who have touched a decision.

    Args:
        history_store: The engine's central history dictionary.
        decision_id: The ID of the decision to look up.

    Returns:
        Ordered list of unique authors (in order of first appearance).
    """
    seen: set[str] = set()
    authors: list[str] = []
    for rev in history_store.get(decision_id, []):
        if rev.author not in seen:
            seen.add(rev.author)
            authors.append(rev.author)
    return authors
