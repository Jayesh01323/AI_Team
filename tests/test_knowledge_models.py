"""
Tests for the Product Knowledge Model (brain.knowledge).

Covers:
- Model construction with defaults
- Model construction with explicit values
- Enum values and string coercion
- Validation (invalid data, out-of-range scores, missing required fields)
- Serialization (model_dump, model_dump_json, round-trip)
- Nested models (ProjectKnowledge with embedded artifacts)
- Schema completeness checking
"""

import pytest
from pydantic import ValidationError

from brain.knowledge import (
    PROJECT_SCHEMA,
    Assumption,
    ConfidenceLevel,
    ConfidenceScore,
    Constraint,
    ConstraintType,
    Decision,
    DecisionStatus,
    KnowledgeSource,
    OpenQuestion,
    ProjectKnowledge,
    ProjectMetadata,
    ProjectState,
    QuestionImportance,
    Requirement,
    RequirementPriority,
    RequirementStatus,
    SchemaSection,
    UserPreference,
    get_optional_sections,
    get_required_sections,
    get_section_names,
    is_complete,
)

# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestEnums:
    """Tests for enum definitions and string values."""

    def test_decision_status_values(self):
        assert DecisionStatus.PENDING == "pending"
        assert DecisionStatus.ACCEPTED == "accepted"
        assert DecisionStatus.REJECTED == "rejected"
        assert DecisionStatus.DEPRECATED == "deprecated"

    def test_requirement_priority_values(self):
        assert RequirementPriority.CRITICAL == "critical"
        assert RequirementPriority.HIGH == "high"
        assert RequirementPriority.MEDIUM == "medium"
        assert RequirementPriority.LOW == "low"

    def test_requirement_status_values(self):
        assert RequirementStatus.PROPOSED == "proposed"
        assert RequirementStatus.APPROVED == "approved"
        assert RequirementStatus.IMPLEMENTED == "implemented"
        assert RequirementStatus.REMOVED == "removed"

    def test_question_importance_values(self):
        assert QuestionImportance.CRITICAL == "critical"
        assert QuestionImportance.HIGH == "high"
        assert QuestionImportance.MEDIUM == "medium"
        assert QuestionImportance.LOW == "low"

    def test_confidence_level_values(self):
        assert ConfidenceLevel.UNKNOWN == "unknown"
        assert ConfidenceLevel.LOW == "low"
        assert ConfidenceLevel.MEDIUM == "medium"
        assert ConfidenceLevel.HIGH == "high"
        assert ConfidenceLevel.CERTAIN == "certain"

    def test_project_state_values(self):
        assert ProjectState.INITIALIZATION == "initialization"
        assert ProjectState.DISCOVERY == "discovery"
        assert ProjectState.PLANNING == "planning"
        assert ProjectState.COMPLETED == "completed"

    def test_constraint_type_values(self):
        assert ConstraintType.BUDGET == "budget"
        assert ConstraintType.TECHNICAL == "technical"
        assert ConstraintType.TIME == "time"
        assert ConstraintType.COMPLIANCE == "compliance"

    def test_knowledge_source_values(self):
        assert KnowledgeSource.USER == "user"
        assert KnowledgeSource.AI_INFERENCE == "ai_inference"
        assert KnowledgeSource.SYSTEM_DEFAULT == "system_default"


# ---------------------------------------------------------------------------
# ConfidenceScore tests
# ---------------------------------------------------------------------------


class TestConfidenceScore:
    """Tests for the ConfidenceScore model."""

    def test_default_construction(self):
        cs = ConfidenceScore()
        assert cs.level == "unknown"
        assert cs.score is None
        assert cs.source == "ai_inference"
        assert cs.reasoning is None

    def test_valid_score_range(self):
        cs = ConfidenceScore(level=ConfidenceLevel.HIGH, score=0.85)
        assert cs.score == 0.85

    def test_score_zero_allowed(self):
        cs = ConfidenceScore(score=0.0)
        assert cs.score == 0.0

    def test_score_one_allowed(self):
        cs = ConfidenceScore(score=1.0)
        assert cs.score == 1.0

    def test_score_below_zero_rejected(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=-0.1)

    def test_score_above_one_rejected(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=1.5)

    def test_string_enum_coercion(self):
        cs = ConfidenceScore(level="high")
        assert cs.level == "high"


# ---------------------------------------------------------------------------
# ProjectMetadata tests
# ---------------------------------------------------------------------------


class TestProjectMetadata:
    """Tests for the ProjectMetadata model."""

    def test_default_construction(self):
        meta = ProjectMetadata()
        assert meta.project_id.startswith("project-")
        assert meta.project_name == ""
        assert meta.version == "0.1.0"
        assert meta.state == "initialization"
        assert meta.tags == []

    def test_custom_construction(self):
        meta = ProjectMetadata(
            project_name="My App",
            version="1.2.0",
            state=ProjectState.PLANNING,
            tags=["web", "saas"],
        )
        assert meta.project_name == "My App"
        assert meta.version == "1.2.0"
        assert meta.state == "planning"
        assert meta.tags == ["web", "saas"]


# ---------------------------------------------------------------------------
# Decision tests
# ---------------------------------------------------------------------------


class TestDecision:
    """Tests for the Decision model."""

    def test_default_construction(self):
        d = Decision(topic="language", value="python")
        assert d.id.startswith("decision-")
        assert d.topic == "language"
        assert d.value == "python"
        assert d.rationale == ""
        assert d.alternatives == []
        assert d.status == "pending"
        assert d.source == "ai_inference"

    def test_full_construction(self):
        d = Decision(
            topic="database",
            value="postgresql",
            rationale="ACID compliance needed",
            alternatives=["mysql", "mongodb"],
            status=DecisionStatus.ACCEPTED,
            source=KnowledgeSource.USER,
            confidence=ConfidenceScore(level=ConfidenceLevel.HIGH, score=0.9),
        )
        assert d.value == "postgresql"
        assert d.alternatives == ["mysql", "mongodb"]
        assert d.status == "accepted"
        assert d.confidence.level == "high"

    def test_empty_topic_rejected(self):
        with pytest.raises(ValidationError):
            Decision(topic="", value="python")

    def test_empty_value_rejected(self):
        with pytest.raises(ValidationError):
            Decision(topic="language", value="")


# ---------------------------------------------------------------------------
# Requirement tests
# ---------------------------------------------------------------------------


class TestRequirement:
    """Tests for the Requirement model."""

    def test_default_construction(self):
        req = Requirement(title="User Authentication")
        assert req.id.startswith("req-")
        assert req.title == "User Authentication"
        assert req.priority == "medium"
        assert req.status == "proposed"
        assert req.dependencies == []
        assert req.source == "user"

    def test_full_construction(self):
        req = Requirement(
            title="API Rate Limiting",
            description="Limit API requests per user",
            priority=RequirementPriority.HIGH,
            status=RequirementStatus.APPROVED,
            dependencies=["req-123"],
            source=KnowledgeSource.USER,
        )
        assert req.priority == "high"
        assert req.status == "approved"
        assert req.dependencies == ["req-123"]

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            Requirement(title="")


# ---------------------------------------------------------------------------
# Constraint tests
# ---------------------------------------------------------------------------


class TestConstraint:
    """Tests for the Constraint model."""

    def test_default_construction(self):
        c = Constraint(name="Budget")
        assert c.id.startswith("constraint-")
        assert c.name == "Budget"
        assert c.type == "other"
        assert c.value is None

    def test_full_construction(self):
        c = Constraint(
            name="Max Budget",
            type=ConstraintType.BUDGET,
            description="Cannot exceed $10,000",
            value="$10,000",
        )
        assert c.type == "budget"
        assert c.value == "$10,000"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            Constraint(name="")


# ---------------------------------------------------------------------------
# Assumption tests
# ---------------------------------------------------------------------------


class TestAssumption:
    """Tests for the Assumption model."""

    def test_default_construction(self):
        a = Assumption(statement="Users have internet access")
        assert a.id.startswith("assumption-")
        assert a.statement == "Users have internet access"
        assert a.validated is False
        assert a.source == "ai_inference"

    def test_validated_assumption(self):
        a = Assumption(statement="Python 3.11 available", validated=True)
        assert a.validated is True

    def test_empty_statement_rejected(self):
        with pytest.raises(ValidationError):
            Assumption(statement="")


# ---------------------------------------------------------------------------
# OpenQuestion tests
# ---------------------------------------------------------------------------


class TestOpenQuestion:
    """Tests for the OpenQuestion model."""

    def test_default_construction(self):
        q = OpenQuestion(question="What is the target deployment?")
        assert q.id.startswith("question-")
        assert q.question == "What is the target deployment?"
        assert q.importance == "medium"
        assert q.blocking is False
        assert q.status == "open"
        assert q.answer is None

    def test_blocking_question(self):
        q = OpenQuestion(
            question="What database?",
            importance=QuestionImportance.CRITICAL,
            blocking=True,
        )
        assert q.blocking is True
        assert q.importance == "critical"

    def test_answered_question(self):
        q = OpenQuestion(
            question="What database?",
            status="answered",
            answer="PostgreSQL",
        )
        assert q.status == "answered"
        assert q.answer == "PostgreSQL"

    def test_empty_question_rejected(self):
        with pytest.raises(ValidationError):
            OpenQuestion(question="")


# ---------------------------------------------------------------------------
# UserPreference tests
# ---------------------------------------------------------------------------


class TestUserPreference:
    """Tests for the UserPreference model."""

    def test_default_construction(self):
        pref = UserPreference(category="language", key="backend", value="python")
        assert pref.id.startswith("pref-")
        assert pref.category == "language"
        assert pref.key == "backend"
        assert pref.value == "python"
        assert pref.source == "user"

    def test_cloud_preference(self):
        pref = UserPreference(category="cloud", key="provider", value="aws")
        assert pref.category == "cloud"
        assert pref.value == "aws"

    def test_empty_category_rejected(self):
        with pytest.raises(ValidationError):
            UserPreference(category="", key="backend", value="python")

    def test_empty_value_rejected(self):
        with pytest.raises(ValidationError):
            UserPreference(category="language", key="backend", value="")


# ---------------------------------------------------------------------------
# ProjectKnowledge (aggregate root) tests
# ---------------------------------------------------------------------------


class TestProjectKnowledge:
    """Tests for the ProjectKnowledge aggregate root."""

    def test_empty_construction(self):
        pk = ProjectKnowledge()
        assert pk.metadata.project_id.startswith("project-")
        assert pk.vision == ""
        assert pk.problem == ""
        assert pk.target_users == []
        assert pk.business_goals == []
        assert pk.functional_requirements == []
        assert pk.non_functional_requirements == []
        assert pk.decisions == []
        assert pk.constraints == []
        assert pk.assumptions == []
        assert pk.open_questions == []
        assert pk.user_preferences == []
        assert pk.architecture_notes == []
        assert pk.deployment_notes == []
        assert pk.testing_notes == []
        assert pk.extra == {}

    def test_nested_models(self):
        pk = ProjectKnowledge(
            vision="AI code reviewer",
            problem="Slow reviews",
            target_users=["devs", "teams"],
            business_goals=["reduce review time"],
            decisions=[
                Decision(topic="lang", value="python", status=DecisionStatus.ACCEPTED),
            ],
            constraints=[
                Constraint(name="Budget", type=ConstraintType.BUDGET, value="$5k"),
            ],
            assumptions=[
                Assumption(statement="Team knows Python"),
            ],
            open_questions=[
                OpenQuestion(question="Which CI?", blocking=True),
            ],
            user_preferences=[
                UserPreference(category="cloud", key="provider", value="aws"),
            ],
            functional_requirements=[
                Requirement(title="Analyze PRs", priority=RequirementPriority.CRITICAL),
            ],
            architecture_notes=["Microservices"],
            deployment_notes=["Docker"],
            testing_notes=["Pytest"],
        )
        assert pk.vision == "AI code reviewer"
        assert len(pk.decisions) == 1
        assert pk.decisions[0].value == "python"
        assert len(pk.constraints) == 1
        assert pk.constraints[0].type == "budget"
        assert len(pk.assumptions) == 1
        assert len(pk.open_questions) == 1
        assert pk.open_questions[0].blocking is True
        assert len(pk.user_preferences) == 1
        assert len(pk.functional_requirements) == 1
        assert pk.functional_requirements[0].priority == "critical"
        assert pk.architecture_notes == ["Microservices"]

    def test_touch_updates_timestamp(self):
        pk = ProjectKnowledge()
        original = pk.metadata.updated_at
        pk.touch()
        assert pk.metadata.updated_at >= original

    def test_extra_field_extensibility(self):
        pk = ProjectKnowledge(extra={"custom_field": "custom_value"})
        assert pk.extra["custom_field"] == "custom_value"


# ---------------------------------------------------------------------------
# Serialization tests
# ---------------------------------------------------------------------------


class TestSerialization:
    """Tests for model serialization and round-trip."""

    def test_confidence_score_serialization(self):
        cs = ConfidenceScore(level=ConfidenceLevel.HIGH, score=0.9)
        data = cs.model_dump()
        assert data["level"] == "high"
        assert data["score"] == 0.9

    def test_decision_serialization(self):
        d = Decision(topic="db", value="postgres")
        data = d.model_dump()
        assert data["topic"] == "db"
        assert data["value"] == "postgres"
        assert data["status"] == "pending"

    def test_project_knowledge_serialization(self):
        pk = ProjectKnowledge(
            vision="Test",
            decisions=[Decision(topic="lang", value="python")],
        )
        data = pk.model_dump()
        assert data["vision"] == "Test"
        assert len(data["decisions"]) == 1
        assert data["decisions"][0]["value"] == "python"

    def test_json_serialization(self):
        pk = ProjectKnowledge(vision="Test")
        json_str = pk.model_dump_json()
        assert '"vision":"Test"' in json_str

    def test_round_trip(self):
        pk = ProjectKnowledge(
            vision="Round Trip",
            problem="Testing",
            target_users=["users"],
            decisions=[
                Decision(
                    topic="framework",
                    value="fastapi",
                    alternatives=["flask", "django"],
                    status=DecisionStatus.ACCEPTED,
                )
            ],
            functional_requirements=[
                Requirement(title="Auth", priority=RequirementPriority.HIGH),
            ],
        )
        data = pk.model_dump()
        restored = ProjectKnowledge(**data)
        assert restored.vision == "Round Trip"
        assert len(restored.decisions) == 1
        assert restored.decisions[0].value == "fastapi"
        assert len(restored.functional_requirements) == 1
        assert restored.functional_requirements[0].priority == "high"

    def test_nested_confidence_round_trip(self):
        pk = ProjectKnowledge(
            decisions=[
                Decision(
                    topic="cloud",
                    value="aws",
                    confidence=ConfidenceScore(
                        level=ConfidenceLevel.HIGH,
                        score=0.92,
                        reasoning="Team experience",
                    ),
                )
            ]
        )
        data = pk.model_dump()
        restored = ProjectKnowledge(**data)
        assert restored.decisions[0].confidence.level == "high"
        assert restored.decisions[0].confidence.score == 0.92


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestSchema:
    """Tests for the project schema definition."""

    def test_schema_has_sections(self):
        assert len(PROJECT_SCHEMA) > 0

    def test_required_sections(self):
        required = get_required_sections()
        names = [s.name for s in required]
        assert "vision" in names
        assert "problem" in names
        assert "functional_requirements" in names

    def test_optional_sections(self):
        optional = get_optional_sections()
        names = [s.name for s in optional]
        assert "architecture" in names
        assert "tech_stack" in names

    def test_section_names(self):
        names = get_section_names()
        assert "vision" in names
        assert "deployment" in names
        assert len(names) == len(PROJECT_SCHEMA)

    def test_schema_section_is_frozen(self):
        section = SchemaSection(name="test", label="Test", description="d")
        with pytest.raises(Exception):
            section.name = "changed"  # type: ignore[misc]

    def test_is_complete_empty_knowledge(self):
        pk = ProjectKnowledge()
        data = pk.model_dump()
        result = is_complete(data)
        assert result["vision"] is False
        assert result["problem"] is False

    def test_is_complete_populated_knowledge(self):
        pk = ProjectKnowledge(
            vision="Test",
            problem="Problem",
            target_users=["users"],
            business_goals=["goal"],
            functional_requirements=[Requirement(title="Req")],
            non_functional_requirements=[Requirement(title="NFR")],
        )
        data = pk.model_dump()
        result = is_complete(data)
        assert result["vision"] is True
        assert result["problem"] is True
        assert result["target_users"] is True
        assert result["functional_requirements"] is True


# ---------------------------------------------------------------------------
# Invalid data tests
# ---------------------------------------------------------------------------


class TestInvalidData:
    """Tests that invalid data is properly rejected."""

    def test_invalid_confidence_score(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=2.0)

    def test_invalid_decision_missing_topic(self):
        with pytest.raises(ValidationError):
            Decision(value="python")  # type: ignore[call-arg]

    def test_invalid_requirement_missing_title(self):
        with pytest.raises(ValidationError):
            Requirement()  # type: ignore[call-arg]

    def test_invalid_constraint_missing_name(self):
        with pytest.raises(ValidationError):
            Constraint()  # type: ignore[call-arg]

    def test_invalid_assumption_missing_statement(self):
        with pytest.raises(ValidationError):
            Assumption()  # type: ignore[call-arg]

    def test_invalid_open_question_missing_question(self):
        with pytest.raises(ValidationError):
            OpenQuestion()  # type: ignore[call-arg]

    def test_invalid_user_preference_missing_fields(self):
        with pytest.raises(ValidationError):
            UserPreference(value="python")  # type: ignore[call-arg]

    def test_invalid_enum_value(self):
        with pytest.raises(ValidationError):
            Decision(topic="x", value="y", status="invalid_status")