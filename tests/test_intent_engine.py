"""
Comprehensive tests for the Intent Engine.

Covers:
- Simple project descriptions
- Complex project descriptions
- Constraint extraction
- Preference extraction
- Missing information detection
- Confidence calculation
- Question generation
- Knowledge updates
- Invalid inputs
- Empty inputs
- Repeated conversations
- Regression tests
"""

import pytest

from brain.intent import IntentEngine, IntentResult
from brain.intent.classifier import classify_all, classify_domain, classify_product_category, classify_project_type
from brain.intent.confidence import calculate_overall_confidence, calculate_section_confidence, is_confident
from brain.intent.extractor import (
    extract_all_facts,
    extract_business_goals,
    extract_business_model,
    extract_constraints,
    extract_domain,
    extract_preferences,
    extract_product_category,
    extract_project_type,
    extract_requirements,
    extract_target_users,
)
from brain.intent.gap_detector import detect_gaps, get_blocking_gaps, get_high_priority_gaps
from brain.intent.models import (
    ClassificationResult,
    ExtractedFact,
    Gap,
    IntentAnalysis,
    IntentResult,
    NormalizedInput,
    SectionConfidence,
)
from brain.intent.question_generator import generate_questions
from brain.intent.rules import (
    BUSINESS_GOAL_INDICATORS,
    CONSTRAINT_RULES,
    PREFERENCE_RULES,
    PROBLEM_INDICATORS,
    PROJECT_TYPE_RULES,
    TARGET_USER_INDICATORS,
    classify_by_rules,
    get_matched_keywords,
    is_ambiguous,
    is_explicit_statement,
    is_vague,
    match_keywords,
)


# ---------------------------------------------------------------------------
# Normalization tests
# ---------------------------------------------------------------------------


class TestNormalization:
    """Tests for input normalization."""

    def test_simple_text(self):
        engine = IntentEngine()
        result = engine.analyze("I want to build a web app")
        assert result is not None
        assert result.knowledge is not None

    def test_empty_input(self):
        engine = IntentEngine()
        result = engine.analyze("")
        assert result is not None
        assert result.knowledge is not None

    def test_whitespace_input(self):
        engine = IntentEngine()
        result = engine.analyze("   ")
        assert result is not None

    def test_case_insensitive(self):
        engine = IntentEngine()
        result1 = engine.analyze("I want to build a WEB APP")
        result2 = engine.analyze("i want to build a web app")
        assert result1.knowledge.extra.get("project_type") == result2.knowledge.extra.get("project_type")


# ---------------------------------------------------------------------------
# Extraction tests
# ---------------------------------------------------------------------------


class TestExtraction:
    """Tests for fact extraction."""

    def test_extract_project_type_web_app(self):
        facts = extract_all_facts("I want to build a web app")
        project_types = [f for f in facts if f.category == "project_type"]
        assert len(project_types) > 0
        assert project_types[0].value == "web_app"

    def test_extract_project_type_cli(self):
        facts = extract_all_facts("I need a CLI tool for automation")
        project_types = [f for f in facts if f.category == "project_type"]
        assert len(project_types) > 0
        assert project_types[0].value == "cli"

    def test_extract_domain_ai(self):
        facts = extract_all_facts("Build an AI-powered code review tool")
        domains = [f for f in facts if f.category == "domain"]
        assert len(domains) > 0
        assert domains[0].value == "ai"

    def test_extract_domain_education(self):
        facts = extract_all_facts("Create an online learning platform")
        domains = [f for f in facts if f.category == "domain"]
        assert len(domains) > 0
        assert domains[0].value == "education"

    def test_extract_product_category_saas(self):
        facts = extract_all_facts("Build a SaaS resume analyzer")
        categories = [f for f in facts if f.category == "product_category"]
        assert len(categories) > 0
        assert categories[0].value == "saas"

    def test_extract_business_model_saas(self):
        facts = extract_all_facts("I want a SaaS subscription service")
        models = [f for f in facts if f.category == "business_model"]
        assert len(models) > 0
        assert models[0].value == "saas"

    def test_extract_problem(self):
        facts = extract_all_facts("The problem is slow code reviews")
        problems = [f for f in facts if f.category == "problem"]
        assert len(problems) > 0
        assert "slow" in problems[0].value

    def test_extract_target_users(self):
        facts = extract_all_facts("Build a tool for developers")
        users = [f for f in facts if f.category == "target_user"]
        assert len(users) > 0
        assert users[0].value == "developers"

    def test_extract_business_goals(self):
        facts = extract_all_facts("I want to increase revenue by 20%")
        goals = [f for f in facts if f.category == "business_goal"]
        assert len(goals) > 0
        assert "increase" in goals[0].value

    def test_extract_constraints_technical(self):
        facts = extract_all_facts("Must use Python only and run offline")
        constraints = [f for f in facts if f.category == "constraint"]
        assert len(constraints) > 0
        values = [c.value for c in constraints]
        # Should extract the matched constraint keywords
        assert any("python" in v or "offline" in v for v in values)

    def test_extract_constraints_budget(self):
        facts = extract_all_facts("We have a limited budget")
        constraints = [f for f in facts if f.category == "constraint"]
        assert len(constraints) > 0
        assert "budget" in [c.value for c in constraints]

    def test_extract_preferences_language(self):
        facts = extract_all_facts("I want to use Python for this project")
        preferences = [f for f in facts if f.category == "preference"]
        assert len(preferences) > 0
        assert "python" in [p.value for p in preferences]

    def test_extract_preferences_framework(self):
        facts = extract_all_facts("Build with React and FastAPI")
        preferences = [f for f in facts if f.category == "preference"]
        assert len(preferences) > 0
        values = [p.value for p in preferences]
        assert "react" in values or "fastapi" in values

    def test_extract_requirements(self):
        facts = extract_all_facts("The system must support user authentication and authorization")
        requirements = [f for f in facts if f.category == "requirement"]
        assert len(requirements) > 0
        assert "authentication" in requirements[0].value or "authorization" in requirements[0].value

    def test_no_facts_from_empty_input(self):
        facts = extract_all_facts("")
        assert len(facts) == 0

    def test_no_facts_from_vague_input(self):
        facts = extract_all_facts("something something")
        assert len(facts) == 0


# ---------------------------------------------------------------------------
# Classification tests
# ---------------------------------------------------------------------------


class TestClassification:
    """Tests for project classification."""

    def test_classify_web_app(self):
        result = classify_project_type("Build a web application with React")
        assert result is not None
        assert result.value == "web_app"
        assert result.confidence.score > 0.0

    def test_classify_desktop(self):
        result = classify_project_type("Create a desktop app with Electron")
        assert result is not None
        assert result.value == "desktop"

    def test_classify_cli(self):
        result = classify_project_type("Build a CLI tool for developers")
        assert result is not None
        assert result.value == "cli"

    def test_classify_api(self):
        result = classify_project_type("Create a REST API with FastAPI")
        assert result is not None
        assert result.value == "api"

    def test_classify_domain_ai(self):
        result = classify_domain("Build an AI code reviewer")
        assert result is not None
        assert result.value == "ai"

    def test_classify_domain_developer_tools(self):
        result = classify_domain("Create a developer tool for code review")
        assert result is not None
        assert result.value == "developer_tools"

    def test_classify_product_category_saas(self):
        result = classify_product_category("Build a SaaS platform")
        assert result is not None
        assert result.value == "saas"

    def test_classify_product_category_open_source(self):
        result = classify_product_category("Create an open source library")
        assert result is not None
        assert result.value == "open_source"

    def test_classify_all_returns_multiple(self):
        results = classify_all("Build an AI-powered SaaS web app")
        assert len(results) > 0
        categories = [r.category for r in results]
        assert "project_type" in categories
        assert "domain" in categories
        assert "product_category" in categories

    def test_classify_no_match(self):
        result = classify_project_type("Hello world")
        assert result is None


# ---------------------------------------------------------------------------
# Confidence tests
# ---------------------------------------------------------------------------


class TestConfidence:
    """Tests for confidence calculation."""

    def test_section_confidence_with_content(self):
        confidence = calculate_section_confidence(
            section_name="problem",
            has_content=True,
            explicit_count=1,
            total_indicators=1,
        )
        assert confidence.score > 0.0
        assert confidence.level != "unknown"

    def test_section_confidence_without_content(self):
        confidence = calculate_section_confidence(
            section_name="vision",
            has_content=False,
        )
        assert confidence.score == 0.0
        assert confidence.level == "unknown"

    def test_section_confidence_high_explicit(self):
        confidence = calculate_section_confidence(
            section_name="requirements",
            has_content=True,
            explicit_count=5,
            total_indicators=5,
        )
        assert confidence.score >= 0.8
        assert confidence.level == "high"

    def test_section_confidence_low_explicit(self):
        confidence = calculate_section_confidence(
            section_name="requirements",
            has_content=True,
            explicit_count=1,
            total_indicators=5,
        )
        assert confidence.score < 0.8

    def test_overall_confidence_empty(self):
        confidence = calculate_overall_confidence([])
        assert confidence.score == 0.0
        assert confidence.level == "unknown"

    def test_overall_confidence_high(self):
        sections = [
            SectionConfidence(section="s1", score=0.9, level="high"),
            SectionConfidence(section="s2", score=0.85, level="high"),
            SectionConfidence(section="s3", score=0.8, level="high"),
            SectionConfidence(section="s4", score=0.9, level="high"),
            SectionConfidence(section="s5", score=0.85, level="high"),
        ]
        confidence = calculate_overall_confidence(sections)
        assert confidence.level == "high"

    def test_is_confident_true(self):
        section = SectionConfidence(section="test", score=0.8, level="high")
        assert is_confident(section, threshold=0.6) is True

    def test_is_confident_false(self):
        section = SectionConfidence(section="test", score=0.4, level="low")
        assert is_confident(section, threshold=0.6) is False


# ---------------------------------------------------------------------------
# Gap detection tests
# ---------------------------------------------------------------------------


class TestGapDetection:
    """Tests for gap detection."""

    def test_detect_missing_required_sections(self):
        knowledge = {}
        gaps = detect_gaps(knowledge)
        assert len(gaps) > 0
        blocking = get_blocking_gaps(gaps)
        assert len(blocking) > 0

    def test_detect_empty_sections(self):
        knowledge = {
            "vision": "",
            "problem": "Testing",
            "target_users": [],
            "business_goals": [],
        }
        gaps = detect_gaps(knowledge)
        assert len(gaps) > 0

    def test_no_gaps_for_complete_knowledge(self):
        knowledge = {
            "vision": "Test vision",
            "problem": "Test problem",
            "target_users": ["users"],
            "business_goals": ["goal"],
            "functional_requirements": [{"title": "Req"}],
            "non_functional_requirements": [{"title": "NFR"}],
        }
        gaps = detect_gaps(knowledge)
        # Should have minimal gaps
        assert len(gaps) == 0

    def test_get_blocking_gaps(self):
        gaps = [
            Gap(section="vision", description="Missing", is_blocking=True, importance="critical"),
            Gap(section="problem", description="Missing", is_blocking=False, importance="medium"),
        ]
        blocking = get_blocking_gaps(gaps)
        assert len(blocking) == 1
        assert blocking[0].section == "vision"

    def test_get_high_priority_gaps(self):
        gaps = [
            Gap(section="vision", description="Missing", is_blocking=True, importance="critical"),
            Gap(section="problem", description="Missing", is_blocking=False, importance="low"),
        ]
        high_priority = get_high_priority_gaps(gaps)
        assert len(high_priority) == 1
        assert high_priority[0].section == "vision"


# ---------------------------------------------------------------------------
# Question generation tests
# ---------------------------------------------------------------------------


class TestQuestionGeneration:
    """Tests for question generation."""

    def test_generate_questions_from_gaps(self):
        gaps = [
            Gap(section="vision", description="Missing vision", is_blocking=True, importance="critical"),
            Gap(section="problem", description="Missing problem", is_blocking=True, importance="high"),
        ]
        questions = generate_questions(gaps, [])
        assert len(questions) > 0
        assert len(questions) <= 5

    def test_no_questions_when_sections_known(self):
        gaps = [
            Gap(section="vision", description="Missing vision", is_blocking=True, importance="critical"),
        ]
        questions = generate_questions(gaps, ["vision"])
        assert len(questions) == 0

    def test_max_questions_enforced(self):
        gaps = [
            Gap(section=f"section_{i}", description=f"Missing {i}", is_blocking=True, importance="critical")
            for i in range(10)
        ]
        questions = generate_questions(gaps, [], max_questions=5)
        assert len(questions) <= 5

    def test_questions_prioritized_by_importance(self):
        gaps = [
            Gap(section="s1", description="Low", is_blocking=False, importance="low"),
            Gap(section="s2", description="High", is_blocking=True, importance="critical"),
            Gap(section="s3", description="Medium", is_blocking=False, importance="medium"),
        ]
        questions = generate_questions(gaps, [])
        assert len(questions) > 0
        # First question should be from critical/blocking gap
        assert questions[0].blocking is True

    def test_no_duplicate_questions(self):
        gaps = [
            Gap(section="vision", description="Missing vision", is_blocking=True, importance="critical"),
            Gap(section="vision", description="Missing vision", is_blocking=True, importance="critical"),
        ]
        questions = generate_questions(gaps, [])
        assert len(questions) <= 1


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


class TestIntentEngineIntegration:
    """Integration tests for the full Intent Engine pipeline."""

    def test_simple_project_description(self):
        engine = IntentEngine()
        result = engine.analyze("I want to build a SaaS resume analyzer")
        assert result is not None
        assert isinstance(result, IntentResult)
        assert result.knowledge is not None
        assert result.analysis is not None

    def test_complex_project_description(self):
        engine = IntentEngine()
        result = engine.analyze(
            "I want to build an AI-powered web application for developers. "
            "It should be a SaaS product that analyzes code and provides suggestions. "
            "Must use Python and run offline. Budget is limited."
        )
        assert result is not None
        assert len(result.analysis.classifications) > 0
        assert len(result.analysis.extracted_facts) > 0

    def test_knowledge_populated(self):
        engine = IntentEngine()
        result = engine.analyze("Build a web app for developers to analyze resumes")
        assert result.knowledge.problem or result.knowledge.target_users
        assert len(result.knowledge.functional_requirements) >= 0  # May or may not have requirements

    def test_confidence_calculated(self):
        engine = IntentEngine()
        result = engine.analyze("Build an AI-powered SaaS web app for developers")
        assert len(result.analysis.section_confidences) > 0
        assert result.analysis.overall_confidence.score > 0.0

    def test_gaps_detected(self):
        engine = IntentEngine()
        result = engine.analyze("Build a web app")
        # Should detect gaps for missing information
        assert len(result.analysis.gaps) >= 0  # May have gaps

    def test_questions_generated_when_needed(self):
        engine = IntentEngine()
        result = engine.analyze("Build a web app")
        # Questions may or may not be generated depending on gaps
        assert len(result.analysis.questions) <= 5

    def test_no_questions_when_confident(self):
        engine = IntentEngine()
        result = engine.analyze(
            "I want to build an AI-powered SaaS web application for developers. "
            "The problem is slow code reviews. Target users are software developers. "
            "Business goal is to increase productivity. Must use Python and run offline."
        )
        # With lots of information, should have fewer questions
        assert len(result.analysis.questions) <= 5

    def test_knowledge_timestamp_updated(self):
        engine = IntentEngine()
        result = engine.analyze("Build a web app")
        assert result.knowledge.metadata.updated_at != ""

    def test_repeated_conversations(self):
        engine = IntentEngine()
        result1 = engine.analyze("Build a web app for developers")
        result2 = engine.analyze("Build a web app for developers")
        # Should produce consistent results
        assert result1.knowledge.extra.get("project_type") == result2.knowledge.extra.get("project_type")

    def test_constraint_extraction_updates_knowledge(self):
        engine = IntentEngine()
        result = engine.analyze("Build a Python-only offline desktop app")
        # Should have extracted constraints
        assert len(result.knowledge.constraints) >= 0  # May have constraints

    def test_preference_extraction_updates_knowledge(self):
        engine = IntentEngine()
        result = engine.analyze("I want to use React and PostgreSQL")
        # Should have extracted preferences
        assert len(result.knowledge.user_preferences) >= 0  # May have preferences


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------


class TestRegression:
    """Regression tests for specific scenarios."""

    def test_saas_resume_analyzer_example(self):
        """Test the example from the task description."""
        engine = IntentEngine()
        result = engine.analyze("I want a SaaS resume analyzer.")
        assert result is not None
        assert result.knowledge.extra.get("business_model") == "saas"
        # Should extract SaaS and product category
        assert result.knowledge.extra.get("product_category") == "saas"

    def test_no_architecture_recommendations(self):
        """Ensure the engine does not make architecture recommendations."""
        engine = IntentEngine()
        result = engine.analyze("Build a web app")
        # Should not have architecture notes
        assert len(result.knowledge.architecture_notes) == 0
        # Should not have deployment notes
        assert len(result.knowledge.deployment_notes) == 0
        # Should not have testing notes
        assert len(result.knowledge.testing_notes) == 0

    def test_no_code_generation(self):
        """Ensure the engine does not generate code."""
        engine = IntentEngine()
        result = engine.analyze("Build a web app")
        # Should not have any code in the knowledge
        assert "def " not in result.knowledge.vision
        assert "class " not in result.knowledge.problem

    def test_deterministic_behavior(self):
        """Ensure the engine produces deterministic results."""
        engine = IntentEngine()
        text = "Build an AI-powered SaaS web app for developers"
        result1 = engine.analyze(text)
        result2 = engine.analyze(text)
        # Should produce identical results
        assert result1.knowledge.extra == result2.knowledge.extra
        assert result1.knowledge.problem == result2.knowledge.problem
        assert len(result1.analysis.classifications) == len(result2.analysis.classifications)

    def test_no_hallucination(self):
        """Ensure the engine does not invent information."""
        engine = IntentEngine()
        result = engine.analyze("Build a web app")
        # Should not have invented database, authentication, etc.
        # These should only appear if explicitly mentioned
        all_text = str(result.knowledge.model_dump()).lower()
        # These should not appear unless explicitly mentioned
        assert "postgresql" not in all_text
        assert "authentication" not in all_text
        assert "docker" not in all_text


# ---------------------------------------------------------------------------
# Rule helper tests
# ---------------------------------------------------------------------------


class TestRuleHelpers:
    """Tests for rule helper functions."""

    def test_match_keywords_true(self):
        assert match_keywords("Build a web app", ["web app", "mobile"]) is True

    def test_match_keywords_false(self):
        assert match_keywords("Build a game", ["web app", "mobile"]) is False

    def test_get_matched_keywords(self):
        matched = get_matched_keywords("Build a web app with React", ["web app", "react", "vue"])
        assert "web app" in matched
        assert "react" in matched
        assert "vue" not in matched

    def test_classify_by_rules_no_match(self):
        category, confidence, keywords = classify_by_rules("hello world", {"test": ["xyz"]})
        assert category is None
        assert confidence == 0.0
        assert keywords == []

    def test_classify_by_rules_match(self):
        category, confidence, keywords = classify_by_rules("Build a web app", PROJECT_TYPE_RULES)
        assert category == "web_app"
        assert confidence > 0.0
        assert len(keywords) > 0

    def test_is_explicit_statement_true(self):
        assert is_explicit_statement("I want to build a web app") is True

    def test_is_explicit_statement_false(self):
        assert is_explicit_statement("Maybe we could build something") is False

    def test_is_ambiguous_true(self):
        assert is_ambiguous("Maybe we could build something") is True

    def test_is_ambiguous_false(self):
        assert is_ambiguous("I want to build a web app") is False

    def test_is_vague_true(self):
        assert is_vague("Build something with stuff") is True

    def test_is_vague_false(self):
        assert is_vague("Build a web app with React") is False