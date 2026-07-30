"""
Decision Engine — the central orchestrator.

Manages the full lifecycle of project decisions:
- Recording new decisions
- Validating required fields
- Detecting duplicates and conflicts
- Supporting version history and audit trails
- Transitioning between lifecycle states
- Searching and listing active decisions

No LLM calls. No persistence beyond the in-memory state.
No planning logic. Fully deterministic.
"""

from __future__ import annotations

import copy
from typing import Any

from brain.decisions.conflict_detector import detect_conflicts
from brain.decisions.history import get_history, get_latest_revision, record_revision
from brain.decisions.merger import apply_rejection, apply_supersession, apply_update
from brain.decisions.models import (
    ConflictReport,
    DecisionEngineState,
    DecisionRecord,
    DecisionStatus,
    Revision,
    ValidationResult,
)
from brain.decisions.validator import validate_decision_data, validate_update_data


class DecisionEngine:
    """
    The Decision Engine manages the complete lifecycle of project decisions.

    Maintains an in-memory store of :class:`~brain.decisions.models.DecisionRecord`
    objects along with an immutable revision history for each decision.

    Usage::

        engine = DecisionEngine()
        record = engine.create_decision({
            "title": "Use PostgreSQL",
            "topic": "primary database",
            "category": "technology",
            "value": "postgresql",
            "rationale": "Best fit for relational data with ACID guarantees.",
        })
        engine.accept_decision(record.id, author="alice", reason="Team agreed.")
        history = engine.get_history(record.id)
    """

    def __init__(self) -> None:
        self._state: DecisionEngineState = DecisionEngineState()

    # ------------------------------------------------------------------
    # Core lifecycle operations
    # ------------------------------------------------------------------

    def create_decision(
        self,
        data: dict[str, Any],
        author: str = "system",
        reason: str = "Initial creation.",
    ) -> DecisionRecord:
        """
        Record a new decision.

        Args:
            data: Dictionary of decision fields. Must include ``title``,
                ``topic``, ``category``, ``value``, and ``rationale``.
            author: Who is creating the decision.
            reason: Why this decision is being recorded.

        Returns:
            The created :class:`~brain.decisions.models.DecisionRecord`.

        Raises:
            ValueError: If validation fails or if the ID already exists.
        """
        # Validate structure
        validation = self.validate_decision(data)
        if not validation.is_valid:
            raise ValueError(
                f"Invalid decision data: {'; '.join(validation.errors)}"
            )

        # Check duplicate ID before building the record
        candidate_id = data.get("id", "")
        if candidate_id and candidate_id in self._state.decisions:
            raise ValueError(
                f"A decision with ID '{candidate_id}' already exists. "
                "Use update_decision() to modify it."
            )

        # Build record with proposed status as default
        record_data = dict(data)
        if "status" not in record_data:
            record_data["status"] = DecisionStatus.PROPOSED.value

        record = DecisionRecord(**record_data)

        # Final uniqueness check (in case pydantic generated a different ID)
        if record.id in self._state.decisions:
            raise ValueError(
                f"Generated ID '{record.id}' collides with existing decision."
            )

        self._state.decisions[record.id] = record

        record_revision(
            history_store=self._state.history,
            decision=record,
            previous_snapshot=None,
            author=author,
            reason=reason,
            action="create",
        )

        return copy.deepcopy(record)

    def update_decision(
        self,
        decision_id: str,
        updates: dict[str, Any],
        author: str = "system",
        reason: str = "",
    ) -> DecisionRecord:
        """
        Apply a partial update to an existing decision.

        Args:
            decision_id: The ID of the decision to update.
            updates: Partial field dictionary. Protected fields are ignored.
            author: Who is making the change.
            reason: Why this change is being made.

        Returns:
            The updated :class:`~brain.decisions.models.DecisionRecord`.

        Raises:
            KeyError: If ``decision_id`` is not found.
            ValueError: If update data is invalid, or if attempting to
                silently override an accepted decision's status.
        """
        decision = self._get_or_raise(decision_id)

        update_validation = validate_update_data(updates)
        if not update_validation.is_valid:
            raise ValueError(
                f"Invalid update data: {'; '.join(update_validation.errors)}"
            )

        previous_snapshot, updated = apply_update(decision, updates)
        updated_with_author = DecisionRecord(
            **{**updated.model_dump(), "author": author}
        )

        self._state.decisions[decision_id] = updated_with_author

        record_revision(
            history_store=self._state.history,
            decision=updated_with_author,
            previous_snapshot=previous_snapshot,
            author=author,
            reason=reason,
            action="update",
        )

        return copy.deepcopy(updated_with_author)

    def accept_decision(
        self,
        decision_id: str,
        author: str = "system",
        reason: str = "",
    ) -> DecisionRecord:
        """
        Transition a decision to ``accepted`` status.

        Args:
            decision_id: The ID of the decision to accept.
            author: Who is accepting the decision.
            reason: Why the decision is being accepted.

        Returns:
            The accepted :class:`~brain.decisions.models.DecisionRecord`.

        Raises:
            KeyError: If ``decision_id`` is not found.
            ValueError: If the decision is in a terminal state.
        """
        decision = self._get_or_raise(decision_id)

        current_status = str(decision.status)
        if current_status in (DecisionStatus.REJECTED.value, DecisionStatus.SUPERSEDED.value):
            raise ValueError(
                f"Cannot accept decision '{decision_id}': "
                f"already in terminal status '{current_status}'."
            )

        previous_snapshot = copy.deepcopy(decision.to_snapshot())

        current_data = decision.model_dump()
        current_data["status"] = DecisionStatus.ACCEPTED.value
        current_data["author"] = author
        current_data["version"] = decision.version + 1
        current_data["updated_at"] = _utc_now_iso()

        accepted = DecisionRecord(**current_data)
        self._state.decisions[decision_id] = accepted

        record_revision(
            history_store=self._state.history,
            decision=accepted,
            previous_snapshot=previous_snapshot,
            author=author,
            reason=reason,
            action="accept",
        )

        return copy.deepcopy(accepted)

    def reject_decision(
        self,
        decision_id: str,
        author: str = "system",
        reason: str = "",
    ) -> DecisionRecord:
        """
        Transition a decision to ``rejected`` status.

        Args:
            decision_id: The ID of the decision to reject.
            author: Who is rejecting the decision.
            reason: Why the decision is being rejected.

        Returns:
            The rejected :class:`~brain.decisions.models.DecisionRecord`.

        Raises:
            KeyError: If ``decision_id`` is not found.
            ValueError: If the decision is already in a terminal state.
        """
        decision = self._get_or_raise(decision_id)
        previous_snapshot, rejected = apply_rejection(decision, reason, author)

        self._state.decisions[decision_id] = rejected

        record_revision(
            history_store=self._state.history,
            decision=rejected,
            previous_snapshot=previous_snapshot,
            author=author,
            reason=reason,
            action="reject",
        )

        return copy.deepcopy(rejected)

    def supersede_decision(
        self,
        old_decision_id: str,
        new_decision_data: dict[str, Any],
        author: str = "system",
        reason: str = "",
    ) -> tuple[DecisionRecord, DecisionRecord]:
        """
        Replace an existing decision with a new one, preserving history.

        The old decision is transitioned to ``superseded`` and the new
        decision is linked to it via ``supersedes`` / ``superseded_by``.

        Args:
            old_decision_id: The ID of the decision being replaced.
            new_decision_data: Data for the replacement decision.
            author: Who is making this change.
            reason: Why the decision is being superseded.

        Returns:
            A tuple of ``(superseded_old, new_decision)``.

        Raises:
            KeyError: If ``old_decision_id`` is not found.
            ValueError: If the old decision is already superseded/rejected,
                or if the new decision data fails validation.
        """
        old_decision = self._get_or_raise(old_decision_id)

        current_status = str(old_decision.status)
        if current_status in (DecisionStatus.REJECTED.value, DecisionStatus.SUPERSEDED.value):
            raise ValueError(
                f"Cannot supersede decision '{old_decision_id}': "
                f"already in terminal status '{current_status}'."
            )

        # Validate new decision data
        validation = self.validate_decision(new_decision_data)
        if not validation.is_valid:
            raise ValueError(
                f"Invalid replacement decision data: {'; '.join(validation.errors)}"
            )

        # Create new decision (with proposed status initially)
        new_data = dict(new_decision_data)
        if "status" not in new_data:
            new_data["status"] = DecisionStatus.PROPOSED.value
        new_data["supersedes"] = old_decision_id

        new_record = DecisionRecord(**new_data)

        if new_record.id in self._state.decisions and new_record.id != old_decision_id:
            raise ValueError(
                f"New decision ID '{new_record.id}' already exists."
            )

        # Link old → new
        prev_snapshot_old, superseded_old = apply_supersession(old_decision, new_record)

        # Store both
        self._state.decisions[old_decision_id] = superseded_old
        self._state.decisions[new_record.id] = new_record

        # Record history for old decision
        record_revision(
            history_store=self._state.history,
            decision=superseded_old,
            previous_snapshot=prev_snapshot_old,
            author=author,
            reason=reason or f"Superseded by '{new_record.id}'.",
            action="supersede",
        )

        # Record history for new decision
        record_revision(
            history_store=self._state.history,
            decision=new_record,
            previous_snapshot=None,
            author=author,
            reason=reason or f"Supersedes '{old_decision_id}'.",
            action="create",
        )

        return copy.deepcopy(superseded_old), copy.deepcopy(new_record)

    # ------------------------------------------------------------------
    # Validation & conflict detection
    # ------------------------------------------------------------------

    def validate_decision(self, data: dict[str, Any]) -> ValidationResult:
        """
        Validate a decision data dictionary against all engine rules.

        Args:
            data: Dictionary representing a candidate decision.

        Returns:
            :class:`~brain.decisions.models.ValidationResult` with ``is_valid``
            and any ``errors``.
        """
        return validate_decision_data(data)

    def detect_conflicts(self, data: dict[str, Any]) -> list[ConflictReport]:
        """
        Detect conflicts between a candidate decision and existing decisions.

        Args:
            data: Dictionary representing the candidate decision.

        Returns:
            List of :class:`~brain.decisions.models.ConflictReport` objects.
            Empty list means no conflicts were detected.
        """
        return detect_conflicts(data, self._state.decisions)

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_history(self, decision_id: str) -> list[Revision]:
        """
        Return the full immutable revision history for a decision.

        Args:
            decision_id: The ID of the decision.

        Returns:
            Ordered list of :class:`~brain.decisions.models.Revision`
            objects (oldest → newest). Empty list if not found.
        """
        return get_history(self._state.history, decision_id)

    def get_latest_revision(self, decision_id: str) -> Revision | None:
        """
        Return the most recent revision for a decision.

        Args:
            decision_id: The ID of the decision.

        Returns:
            Latest :class:`~brain.decisions.models.Revision` or ``None``.
        """
        return get_latest_revision(self._state.history, decision_id)

    # ------------------------------------------------------------------
    # Query operations
    # ------------------------------------------------------------------

    def list_active(self) -> list[DecisionRecord]:
        """
        Return all decisions that are not in a terminal state.

        Active decisions have status ``proposed`` or ``accepted``.

        Returns:
            List of :class:`~brain.decisions.models.DecisionRecord` objects.
        """
        terminal = {DecisionStatus.REJECTED.value, DecisionStatus.SUPERSEDED.value}
        return [
            copy.deepcopy(d)
            for d in self._state.decisions.values()
            if str(d.status) not in terminal
        ]

    def list_all(self) -> list[DecisionRecord]:
        """
        Return all decisions including terminal ones.

        Returns:
            List of all :class:`~brain.decisions.models.DecisionRecord` objects.
        """
        return [copy.deepcopy(d) for d in self._state.decisions.values()]

    def get_decision(self, decision_id: str) -> DecisionRecord | None:
        """
        Return a single decision by ID.

        Args:
            decision_id: The decision ID to look up.

        Returns:
            :class:`~brain.decisions.models.DecisionRecord` or ``None``.
        """
        decision = self._state.decisions.get(decision_id)
        return copy.deepcopy(decision) if decision else None

    def search(
        self,
        query: str = "",
        category: str | None = None,
        status: str | None = None,
    ) -> list[DecisionRecord]:
        """
        Search decisions by query text, category, and/or status.

        Args:
            query: Text to search in ``title``, ``topic``, ``value``,
                and ``rationale`` (case-insensitive). Empty string matches all.
            category: Filter by exact category (case-insensitive). ``None``
                matches all categories.
            status: Filter by exact status value. ``None`` matches all statuses.

        Returns:
            List of matching :class:`~brain.decisions.models.DecisionRecord`
            objects.
        """
        query_lower = query.lower().strip()
        category_lower = category.lower().strip() if category else None
        status_lower = status.lower().strip() if status else None

        results: list[DecisionRecord] = []

        for decision in self._state.decisions.values():
            if not self._matches_query(decision, query_lower):
                continue
            if category_lower and decision.category.lower().strip() != category_lower:
                continue
            if status_lower and str(decision.status).lower() != status_lower:
                continue
            results.append(copy.deepcopy(decision))

        return results

    # ------------------------------------------------------------------
    # State inspection
    # ------------------------------------------------------------------

    def decision_count(self) -> int:
        """Return the total number of decisions in the engine."""
        return len(self._state.decisions)

    def active_count(self) -> int:
        """Return the number of active (non-terminal) decisions."""
        return len(self.list_active())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, decision_id: str) -> DecisionRecord:
        """Retrieve a decision or raise KeyError if not found."""
        decision = self._state.decisions.get(decision_id)
        if decision is None:
            raise KeyError(f"Decision '{decision_id}' not found.")
        return decision

    @staticmethod
    def _matches_query(decision: DecisionRecord, query_lower: str) -> bool:
        """Return True if the query matches any searchable field."""
        if not query_lower:
            return True
        searchable = (
            f"{decision.title} {decision.topic} {decision.value} "
            f"{decision.rationale} {decision.category}"
        ).lower()
        return query_lower in searchable


# ---------------------------------------------------------------------------
# Module-level helper
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    from datetime import UTC, datetime
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
