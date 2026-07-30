"""
Comprehensive unit tests for the Decision Engine.

Covers:
- Decision creation and defaults
- Validation (required fields, confidence, status, duplicates)
- Conflict detection (topic, category, technology, architecture)
- Update operations (partial updates, protected fields)
- Lifecycle transitions (accept, reject, supersede)
- Immutable history (append-only, defensive copies)
- Search and list operations
- Edge cases (empty strings, boundary confidence values, etc.)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from brain.decisions import (
    ConflictReport,
    ConflictSeverity,
    ConflictType,
    DecisionEngine,
    DecisionStatus,
)
from brain.decisions.history import (
    list_all_authors,
    revision_count,
)
from brain.decisions.validator import validate_decision_data, validate_update_data
from brain.knowledge import ConfidenceLevel, ConfidenceScore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _base_decision_data(**overrides) -> dict:
    """Return a minimal valid decision data dictionary."""
    defaults = {
        "title": "Use PostgreSQL",
        "topic": "primary database",
        "category": "technology",
        "value": "postgresql",
        "rationale": "Best relational DB for our use case.",
    }
    defaults.update(overrides)
    return defaults


def _make_engine() -> DecisionEngine:
    """Return a fresh DecisionEngine instance."""
    return DecisionEngine()


# ---------------------------------------------------------------------------
# TestDecisionCreation
# ---------------------------------------------------------------------------


class TestDecisionCreation:
    """Tests for create_decision()."""

    def test_create_minimal_decision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())

        assert record.title == "Use PostgreSQL"
        assert record.topic == "primary database"
        assert record.category == "technology"
        assert record.value == "postgresql"
        assert str(record.status) == DecisionStatus.PROPOSED.value
        assert record.version == 1
        assert record.id is not None
        assert record.timestamp is not None

    def test_create_sets_proposed_status_by_default(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        assert str(record.status) == "proposed"

    def test_create_allows_explicit_status(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(status="accepted"))
        assert str(record.status) == "accepted"

    def test_create_sets_author(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(), author="alice")
        # author tracked in history
        history = engine.get_history(record.id)
        assert history[0].author == "alice"

    def test_create_records_initial_revision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        history = engine.get_history(record.id)

        assert len(history) == 1
        assert history[0].version == 1
        assert history[0].action == "create"
        assert history[0].previous_value is None

    def test_create_with_custom_id(self):
        engine = _make_engine()
        data = _base_decision_data(id="custom-id-001")
        record = engine.create_decision(data)
        assert record.id == "custom-id-001"

    def test_create_with_links(self):
        engine = _make_engine()
        data = _base_decision_data(
            linked_requirements=["req-001"],
            linked_constraints=["con-001"],
            linked_assumptions=["asm-001"],
            linked_questions=["q-001"],
        )
        record = engine.create_decision(data)
        assert "req-001" in record.linked_requirements
        assert "con-001" in record.linked_constraints
        assert "asm-001" in record.linked_assumptions
        assert "q-001" in record.linked_questions

    def test_create_with_alternatives(self):
        engine = _make_engine()
        data = _base_decision_data(alternatives=["mysql", "sqlite"])
        record = engine.create_decision(data)
        assert "mysql" in record.alternatives

    def test_create_increments_decision_count(self):
        engine = _make_engine()
        assert engine.decision_count() == 0
        engine.create_decision(_base_decision_data())
        assert engine.decision_count() == 1
        engine.create_decision(_base_decision_data(title="Another Decision", topic="topic-b", value="val-b"))
        assert engine.decision_count() == 2

    def test_create_returns_deep_copy(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        # Mutating the returned record should not affect internal state
        original_id = record.id
        fetched = engine.get_decision(original_id)
        assert fetched is not None
        assert fetched.id == original_id


# ---------------------------------------------------------------------------
# TestValidation
# ---------------------------------------------------------------------------


class TestValidation:
    """Tests for validate_decision() and validate_decision_data()."""

    def test_valid_data_passes(self):
        engine = _make_engine()
        result = engine.validate_decision(_base_decision_data())
        assert result.is_valid is True
        assert result.errors == []

    def test_missing_title_fails(self):
        data = _base_decision_data()
        del data["title"]
        result = validate_decision_data(data)
        assert result.is_valid is False
        assert any("title" in e for e in result.errors)

    def test_missing_topic_fails(self):
        data = _base_decision_data()
        del data["topic"]
        result = validate_decision_data(data)
        assert result.is_valid is False
        assert any("topic" in e for e in result.errors)

    def test_missing_category_fails(self):
        data = _base_decision_data()
        del data["category"]
        result = validate_decision_data(data)
        assert result.is_valid is False
        assert any("category" in e for e in result.errors)

    def test_missing_rationale_fails(self):
        data = _base_decision_data()
        del data["rationale"]
        result = validate_decision_data(data)
        assert result.is_valid is False
        assert any("rationale" in e for e in result.errors)

    def test_missing_value_fails(self):
        data = _base_decision_data()
        del data["value"]
        result = validate_decision_data(data)
        assert result.is_valid is False
        assert any("value" in e for e in result.errors)

    def test_empty_title_fails(self):
        result = validate_decision_data(_base_decision_data(title=""))
        assert result.is_valid is False

    def test_whitespace_title_fails(self):
        result = validate_decision_data(_base_decision_data(title="   "))
        assert result.is_valid is False

    def test_invalid_status_fails(self):
        result = validate_decision_data(_base_decision_data(status="approved"))
        assert result.is_valid is False
        assert any("status" in e for e in result.errors)

    def test_valid_status_values(self):
        for status in ["proposed", "accepted", "rejected", "superseded"]:
            result = validate_decision_data(_base_decision_data(status=status))
            assert result.is_valid is True, f"Status '{status}' should be valid"

    def test_confidence_score_out_of_range_fails(self):
        result = validate_decision_data(_base_decision_data(confidence=1.5))
        assert result.is_valid is False
        assert any("score" in e or "0.0" in e or "range" in e for e in result.errors)

    def test_confidence_score_negative_fails(self):
        result = validate_decision_data(_base_decision_data(confidence=-0.1))
        assert result.is_valid is False

    def test_confidence_score_boundary_values(self):
        for score in [0.0, 0.5, 1.0]:
            result = validate_decision_data(_base_decision_data(confidence=score))
            assert result.is_valid is True, f"Score {score} should be valid"

    def test_confidence_as_dict(self):
        result = validate_decision_data(
            _base_decision_data(confidence={"score": 0.8, "level": "high"})
        )
        assert result.is_valid is True

    def test_confidence_dict_out_of_range_fails(self):
        result = validate_decision_data(
            _base_decision_data(confidence={"score": 2.0, "level": "high"})
        )
        assert result.is_valid is False

    def test_multiple_errors_collected(self):
        result = validate_decision_data({"title": "", "topic": "", "category": "", "value": "", "rationale": ""})
        assert result.is_valid is False
        assert len(result.errors) >= 5

    def test_create_invalid_raises_value_error(self):
        engine = _make_engine()
        with pytest.raises(ValueError, match="Invalid decision data"):
            engine.create_decision({"title": "", "topic": "x", "category": "y", "value": "z", "rationale": "r"})

    def test_validate_update_data_empty_raises(self):
        result = validate_update_data({})
        assert result.is_valid is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_validate_update_data_empty_string_field(self):
        result = validate_update_data({"title": ""})
        assert result.is_valid is False

    def test_validate_update_data_valid_partial(self):
        result = validate_update_data({"title": "New Title", "rationale": "Better reason."})
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# TestDuplicateDetection
# ---------------------------------------------------------------------------


class TestDuplicateDetection:
    """Tests for duplicate ID detection."""

    def test_duplicate_id_raises(self):
        engine = _make_engine()
        data = _base_decision_data(id="dup-001")
        engine.create_decision(data)

        with pytest.raises(ValueError, match="dup-001"):
            engine.create_decision(data)

    def test_duplicate_id_detected_by_detect_conflicts(self):
        engine = _make_engine()
        data = _base_decision_data(id="dup-002")
        engine.create_decision(data)

        conflicts = engine.detect_conflicts(data)
        assert any(c.conflict_type == ConflictType.DUPLICATE_ID for c in conflicts)

    def test_different_ids_no_duplicate(self):
        engine = _make_engine()
        engine.create_decision(_base_decision_data())
        engine.create_decision(_base_decision_data(title="Another", topic="api style", value="rest"))
        assert engine.decision_count() == 2


# ---------------------------------------------------------------------------
# TestConflictDetection
# ---------------------------------------------------------------------------


class TestConflictDetection:
    """Tests for detect_conflicts()."""

    def test_no_conflict_for_different_topics(self):
        engine = _make_engine()
        d = engine.create_decision(_base_decision_data())
        engine.accept_decision(d.id)

        candidate = _base_decision_data(topic="cache layer", value="redis")
        conflicts = engine.detect_conflicts(candidate)
        assert not any(c.conflict_type == ConflictType.TOPIC_CONFLICT for c in conflicts)

    def test_topic_conflict_detected_against_accepted(self):
        engine = _make_engine()
        d = engine.create_decision(_base_decision_data())
        engine.accept_decision(d.id)

        # Same topic, different value
        candidate = _base_decision_data(value="mysql")
        conflicts = engine.detect_conflicts(candidate)
        topic_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.TOPIC_CONFLICT]
        assert len(topic_conflicts) >= 1
        assert topic_conflicts[0].existing_decision_id == d.id

    def test_no_topic_conflict_against_proposed(self):
        engine = _make_engine()
        engine.create_decision(_base_decision_data())
        # Not accepted — should not trigger conflict

        candidate = _base_decision_data(value="mysql")
        conflicts = engine.detect_conflicts(candidate)
        topic_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.TOPIC_CONFLICT]
        assert len(topic_conflicts) == 0

    def test_no_conflict_same_topic_same_value(self):
        engine = _make_engine()
        d = engine.create_decision(_base_decision_data())
        engine.accept_decision(d.id)

        candidate = _base_decision_data(value="postgresql")
        conflicts = engine.detect_conflicts(candidate)
        topic_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.TOPIC_CONFLICT]
        assert len(topic_conflicts) == 0

    def test_architecture_conflict_detected(self):
        engine = _make_engine()
        d = engine.create_decision(
            _base_decision_data(
                title="Use Microservices",
                topic="system architecture",
                category="architecture",
                value="microservices",
                rationale="Scalability.",
            )
        )
        engine.accept_decision(d.id)

        candidate = _base_decision_data(
            title="Use Monolith",
            topic="system architecture",
            category="architecture",
            value="monolith",
            rationale="Simplicity.",
        )
        conflicts = engine.detect_conflicts(candidate)
        arch_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.ARCHITECTURE_CONFLICT]
        assert len(arch_conflicts) >= 1
        assert arch_conflicts[0].severity == ConflictSeverity.CRITICAL

    def test_technology_slot_conflict_detected(self):
        engine = _make_engine()
        d = engine.create_decision(
            _base_decision_data(
                title="Python Backend",
                topic="backend language",
                category="technology",
                value="python",
                rationale="Team expertise.",
            )
        )
        engine.accept_decision(d.id)

        candidate = _base_decision_data(
            title="Go Backend",
            topic="backend language",
            category="technology",
            value="go",
            rationale="Performance.",
        )
        conflicts = engine.detect_conflicts(candidate)
        tech_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.TECHNOLOGY_CONFLICT]
        assert len(tech_conflicts) >= 1

    def test_conflict_returns_structured_report(self):
        engine = _make_engine()
        d = engine.create_decision(_base_decision_data())
        engine.accept_decision(d.id)

        candidate = _base_decision_data(value="mysql")
        conflicts = engine.detect_conflicts(candidate)
        assert all(isinstance(c, ConflictReport) for c in conflicts)

    def test_detect_conflicts_does_not_modify_state(self):
        engine = _make_engine()
        d = engine.create_decision(_base_decision_data())
        engine.accept_decision(d.id)
        count_before = engine.decision_count()

        candidate = _base_decision_data(value="mysql")
        engine.detect_conflicts(candidate)
        assert engine.decision_count() == count_before

    def test_no_conflicts_on_empty_engine(self):
        engine = _make_engine()
        conflicts = engine.detect_conflicts(_base_decision_data())
        assert conflicts == []


# ---------------------------------------------------------------------------
# TestUpdateDecision
# ---------------------------------------------------------------------------


class TestUpdateDecision:
    """Tests for update_decision()."""

    def test_update_title(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        updated = engine.update_decision(record.id, {"title": "New Title"}, reason="Renamed")
        assert updated.title == "New Title"

    def test_update_increments_version(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        updated = engine.update_decision(record.id, {"title": "Updated"})
        assert updated.version == 2

    def test_update_records_revision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.update_decision(record.id, {"title": "Updated"}, reason="Fix typo")
        history = engine.get_history(record.id)
        assert len(history) == 2
        assert history[1].action == "update"
        assert history[1].reason == "Fix typo"

    def test_update_preserves_previous_snapshot(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.update_decision(record.id, {"title": "Updated"})
        history = engine.get_history(record.id)
        assert history[1].previous_value is not None
        assert history[1].previous_value["title"] == "Use PostgreSQL"

    def test_update_protected_fields_ignored(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        original_id = record.id
        original_timestamp = record.timestamp

        updated = engine.update_decision(
            record.id,
            {"id": "hacked-id", "timestamp": "1970-01-01T00:00:00Z"},
        )
        assert updated.id == original_id
        assert updated.timestamp == original_timestamp

    def test_update_nonexistent_raises(self):
        engine = _make_engine()
        with pytest.raises(KeyError):
            engine.update_decision("nonexistent-id", {"title": "X"})

    def test_update_accepted_status_raises(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.accept_decision(record.id)

        with pytest.raises(ValueError, match="silently overwrite"):
            engine.update_decision(record.id, {"status": "rejected"})

    def test_update_proposed_decision_allowed(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        updated = engine.update_decision(record.id, {"rationale": "Better reasoning."})
        assert updated.rationale == "Better reasoning."

    def test_update_empty_payload_raises(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        with pytest.raises(ValueError, match="Invalid update data"):
            engine.update_decision(record.id, {})


# ---------------------------------------------------------------------------
# TestDecisionLifecycle
# ---------------------------------------------------------------------------


class TestDecisionLifecycle:
    """Tests for accept_decision(), reject_decision(), supersede_decision()."""

    def test_accept_proposed_decision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        accepted = engine.accept_decision(record.id, author="bob", reason="Agreed.")
        assert str(accepted.status) == "accepted"

    def test_accept_records_revision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.accept_decision(record.id, reason="Approved")
        history = engine.get_history(record.id)
        assert history[-1].action == "accept"
        assert history[-1].reason == "Approved"

    def test_accept_terminal_raises(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.reject_decision(record.id)
        with pytest.raises(ValueError, match="terminal status"):
            engine.accept_decision(record.id)

    def test_reject_proposed_decision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        rejected = engine.reject_decision(record.id, author="carol", reason="Too costly.")
        assert str(rejected.status) == "rejected"
        assert rejected.rejection_reason == "Too costly."

    def test_reject_records_revision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.reject_decision(record.id, reason="Not feasible")
        history = engine.get_history(record.id)
        assert history[-1].action == "reject"

    def test_reject_accepted_decision(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.accept_decision(record.id)
        rejected = engine.reject_decision(record.id, reason="Changed requirements.")
        assert str(rejected.status) == "rejected"

    def test_reject_already_rejected_raises(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.reject_decision(record.id)
        with pytest.raises(ValueError, match="terminal status"):
            engine.reject_decision(record.id)

    def test_reject_superseded_raises(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        new_data = _base_decision_data(title="MySQL", value="mysql")
        _superseded_old, _ = engine.supersede_decision(old.id, new_data)
        with pytest.raises(ValueError, match="terminal status"):
            engine.reject_decision(old.id)

    def test_supersede_creates_two_decisions(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        new_data = _base_decision_data(title="MySQL Decision", value="mysql", topic="primary database")
        superseded_old, new_dec = engine.supersede_decision(old.id, new_data)

        assert str(superseded_old.status) == "superseded"
        assert superseded_old.superseded_by == new_dec.id
        assert new_dec.supersedes == old.id

    def test_supersede_records_history_for_both(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        new_data = _base_decision_data(title="MySQL", value="mysql", topic="primary database")
        _superseded_old, new_dec = engine.supersede_decision(old.id, new_data, reason="Changed mind")

        old_history = engine.get_history(old.id)
        new_history = engine.get_history(new_dec.id)
        assert any(r.action == "supersede" for r in old_history)
        assert any(r.action == "create" for r in new_history)

    def test_supersede_terminal_decision_raises(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        engine.reject_decision(old.id)

        new_data = _base_decision_data(title="MySQL", value="mysql")
        with pytest.raises(ValueError, match="terminal status"):
            engine.supersede_decision(old.id, new_data)

    def test_supersede_invalid_new_data_raises(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        with pytest.raises(ValueError, match="Invalid replacement"):
            engine.supersede_decision(old.id, {"title": ""})


# ---------------------------------------------------------------------------
# TestHistory
# ---------------------------------------------------------------------------


class TestHistory:
    """Tests for immutable history management."""

    def test_get_history_returns_ordered_revisions(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.update_decision(record.id, {"title": "V2"})
        engine.update_decision(record.id, {"title": "V3"})

        history = engine.get_history(record.id)
        assert len(history) == 3
        assert history[0].version == 1
        assert history[1].version == 2
        assert history[2].version == 3

    def test_get_history_returns_copy_not_reference(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        history = engine.get_history(record.id)
        assert len(history) == 1

        # Mutating the returned list should not affect internal state
        history.clear()
        fresh_history = engine.get_history(record.id)
        assert len(fresh_history) == 1

    def test_history_is_immutable_frozen_model(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        history = engine.get_history(record.id)
        revision = history[0]

        # Revision is a frozen Pydantic model — raises ValidationError or TypeError
        with pytest.raises((ValidationError, TypeError)):
            revision.author = "hacker"  # type: ignore[misc]

    def test_history_empty_for_unknown_id(self):
        engine = _make_engine()
        history = engine.get_history("nonexistent")
        assert history == []

    def test_revision_count_grows_with_each_change(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        assert revision_count(engine._state.history, record.id) == 1

        engine.update_decision(record.id, {"title": "V2"})
        assert revision_count(engine._state.history, record.id) == 2

        engine.accept_decision(record.id)
        assert revision_count(engine._state.history, record.id) == 3

    def test_latest_revision_reflects_most_recent_action(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.accept_decision(record.id, reason="Approved")

        latest = engine.get_latest_revision(record.id)
        assert latest is not None
        assert latest.action == "accept"

    def test_revision_contains_previous_and_new_value(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.update_decision(record.id, {"title": "Updated Title"})

        history = engine.get_history(record.id)
        update_rev = history[1]

        assert update_rev.previous_value["title"] == "Use PostgreSQL"
        assert update_rev.new_value["title"] == "Updated Title"

    def test_list_all_authors(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(), author="alice")
        engine.update_decision(record.id, {"title": "V2"}, author="bob")
        engine.accept_decision(record.id, author="carol")

        authors = list_all_authors(engine._state.history, record.id)
        assert "alice" in authors
        assert "bob" in authors
        assert "carol" in authors


# ---------------------------------------------------------------------------
# TestSearchAndList
# ---------------------------------------------------------------------------


class TestSearchAndList:
    """Tests for list_active(), list_all(), search(), and get_decision()."""

    def test_list_active_returns_proposed_and_accepted(self):
        engine = _make_engine()
        p = engine.create_decision(_base_decision_data(title="P", topic="t-p", value="v-p"))
        a = engine.create_decision(_base_decision_data(title="A", topic="t-a", value="v-a"))
        engine.accept_decision(a.id)

        active = engine.list_active()
        ids = [d.id for d in active]
        assert p.id in ids
        assert a.id in ids

    def test_list_active_excludes_rejected(self):
        engine = _make_engine()
        r = engine.create_decision(_base_decision_data())
        engine.reject_decision(r.id)

        active = engine.list_active()
        ids = [d.id for d in active]
        assert r.id not in ids

    def test_list_active_excludes_superseded(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        new_data = _base_decision_data(title="MySQL", value="mysql", topic="primary database")
        engine.supersede_decision(old.id, new_data)

        active = engine.list_active()
        ids = [d.id for d in active]
        assert old.id not in ids

    def test_list_all_includes_terminal(self):
        engine = _make_engine()
        r = engine.create_decision(_base_decision_data())
        engine.reject_decision(r.id)

        all_decisions = engine.list_all()
        ids = [d.id for d in all_decisions]
        assert r.id in ids

    def test_get_decision_returns_correct_record(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        fetched = engine.get_decision(record.id)
        assert fetched is not None
        assert fetched.id == record.id

    def test_get_decision_returns_none_for_unknown(self):
        engine = _make_engine()
        assert engine.get_decision("unknown") is None

    def test_search_by_query_text(self):
        engine = _make_engine()
        pg = engine.create_decision(_base_decision_data())
        redis = engine.create_decision(
            _base_decision_data(title="Use Redis", topic="cache layer", value="redis", rationale="Fast in-memory cache.")
        )

        results = engine.search(query="redis")
        ids = [d.id for d in results]
        assert redis.id in ids
        assert pg.id not in ids

    def test_search_empty_query_returns_all(self):
        engine = _make_engine()
        engine.create_decision(_base_decision_data())
        engine.create_decision(_base_decision_data(title="Redis", topic="cache", value="redis"))
        results = engine.search(query="")
        assert len(results) == 2

    def test_search_by_category(self):
        engine = _make_engine()
        tech = engine.create_decision(_base_decision_data(category="technology"))
        arch = engine.create_decision(
            _base_decision_data(title="Microservices", topic="design pattern", category="architecture", value="microservices")
        )

        results = engine.search(category="architecture")
        ids = [d.id for d in results]
        assert arch.id in ids
        assert tech.id not in ids

    def test_search_by_status(self):
        engine = _make_engine()
        p = engine.create_decision(_base_decision_data())
        a = engine.create_decision(_base_decision_data(title="A", topic="t-a", value="v-a"))
        engine.accept_decision(a.id)

        accepted_results = engine.search(status="accepted")
        ids = [d.id for d in accepted_results]
        assert a.id in ids
        assert p.id not in ids

    def test_search_combined_filters(self):
        engine = _make_engine()
        engine.create_decision(_base_decision_data())
        redis = engine.create_decision(
            _base_decision_data(title="Redis Cache", topic="cache", category="technology", value="redis")
        )
        engine.accept_decision(redis.id)

        results = engine.search(query="redis", category="technology", status="accepted")
        assert len(results) == 1
        assert results[0].id == redis.id

    def test_search_case_insensitive(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        results = engine.search(query="POSTGRESQL")
        assert any(d.id == record.id for d in results)


# ---------------------------------------------------------------------------
# TestConfidenceHandling
# ---------------------------------------------------------------------------


class TestConfidenceHandling:
    """Tests for confidence score validation and coercion."""

    def test_float_confidence_coerced_to_confidence_score(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(confidence=0.8))
        assert record.confidence.score == pytest.approx(0.8)

    def test_high_confidence_mapped_to_high_level(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(confidence=0.9))
        assert str(record.confidence.level) in ("certain", "high")

    def test_low_confidence_mapped_to_low_level(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(confidence=0.2))
        assert str(record.confidence.level) == "low"

    def test_zero_confidence_mapped_to_unknown(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(confidence=0.0))
        assert str(record.confidence.level) == "unknown"

    def test_confidence_score_object_accepted(self):
        engine = _make_engine()
        conf = ConfidenceScore(score=0.75, level=ConfidenceLevel.HIGH)
        record = engine.create_decision(_base_decision_data(confidence=conf))
        assert record.confidence.score == pytest.approx(0.75)

    def test_confidence_out_of_range_rejected(self):
        with pytest.raises(ValueError):
            engine = _make_engine()
            engine.create_decision(_base_decision_data(confidence=1.1))


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_create_then_immediately_accept(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        accepted = engine.accept_decision(record.id)
        assert str(accepted.status) == "accepted"

    def test_multiple_updates_sequential(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.update_decision(record.id, {"title": "V2"})
        engine.update_decision(record.id, {"title": "V3"})
        engine.update_decision(record.id, {"title": "V4"})

        history = engine.get_history(record.id)
        assert len(history) == 4
        assert history[-1].new_value["title"] == "V4"

    def test_search_no_results(self):
        engine = _make_engine()
        engine.create_decision(_base_decision_data())
        results = engine.search(query="xyz_nonexistent_12345")
        assert results == []

    def test_active_count_with_mix(self):
        engine = _make_engine()
        engine.create_decision(_base_decision_data())
        r = engine.create_decision(_base_decision_data(title="R", topic="t-r", value="v-r"))
        engine.reject_decision(r.id)

        assert engine.active_count() == 1

    def test_version_chain_maintained_through_supersession(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        assert old.version == 1

        new_data = _base_decision_data(title="MySQL", value="mysql", topic="primary database")
        superseded_old, new_dec = engine.supersede_decision(old.id, new_data)

        # Old should have been versioned up
        assert superseded_old.version > 1
        # New starts at version 1
        assert new_dec.version == 1

    def test_decision_count_after_supersession(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        new_data = _base_decision_data(title="MySQL", value="mysql", topic="primary database")
        engine.supersede_decision(old.id, new_data)

        # Both old (superseded) and new are stored
        assert engine.decision_count() == 2

    def test_large_number_of_decisions(self):
        engine = _make_engine()
        for i in range(50):
            engine.create_decision(
                _base_decision_data(title=f"Decision {i}", topic=f"topic-{i}", value=f"value-{i}")
            )
        assert engine.decision_count() == 50
        assert len(engine.list_active()) == 50

    def test_reject_then_supersede_raises(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        engine.reject_decision(record.id)

        new_data = _base_decision_data(title="MySQL", value="mysql")
        with pytest.raises(ValueError, match="terminal status"):
            engine.supersede_decision(record.id, new_data)

    def test_confidence_boundary_exact_1(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(confidence=1.0))
        assert record.confidence.score == pytest.approx(1.0)

    def test_confidence_boundary_exact_0(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data(confidence=0.0))
        assert record.confidence.score == pytest.approx(0.0)

    def test_get_history_for_superseded_decision(self):
        engine = _make_engine()
        old = engine.create_decision(_base_decision_data())
        new_data = _base_decision_data(title="MySQL", value="mysql", topic="primary database")
        engine.supersede_decision(old.id, new_data, reason="Switching DB")

        history = engine.get_history(old.id)
        assert len(history) >= 2
        # Last action should be supersede
        assert any(r.action == "supersede" for r in history)

    def test_links_survive_update(self):
        engine = _make_engine()
        record = engine.create_decision(
            _base_decision_data(linked_requirements=["req-001"])
        )
        updated = engine.update_decision(record.id, {"title": "Updated"})
        assert "req-001" in updated.linked_requirements

    def test_no_conflict_when_engine_empty(self):
        engine = _make_engine()
        conflicts = engine.detect_conflicts(_base_decision_data())
        assert conflicts == []

    def test_conflict_type_is_enum(self):
        engine = _make_engine()
        d = engine.create_decision(_base_decision_data())
        engine.accept_decision(d.id)
        conflicts = engine.detect_conflicts(_base_decision_data(value="mysql"))
        for c in conflicts:
            assert isinstance(c.conflict_type, str)  # str enum

    def test_accept_decision_increments_version(self):
        engine = _make_engine()
        record = engine.create_decision(_base_decision_data())
        accepted = engine.accept_decision(record.id)
        assert accepted.version == 2
