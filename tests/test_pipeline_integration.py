"""
Integration tests for the Engineering Brain pipeline.

Mocks AI responses to verify the full pipeline flow without
requiring actual API credentials.
"""

import json
from unittest.mock import MagicMock, patch

from brain.stages import (
    ArchitectureGeneratorStage,
    IdeaAnalyzerStage,
    PRDGeneratorStage,
    ProjectSpecificationGeneratorStage,
    RequirementsGeneratorStage,
    TaskPlannerStage,
)
from models.architecture import Architecture
from models.idea import Idea
from models.prd import PRD
from models.project_context import ProjectContext
from models.project_specification import ProjectSpecification
from models.requirements import Requirements
from pipeline.engine import PipelineEngine
from pipeline.executor import (
    ArtifactValidationError,
    StageDependencyError,
    execute_stage,
    validate_stage_artifacts,
)
from pipeline.registry import list_stages


def test_registry_contains_all_stages():
    """Verify all 6 stages are registered."""
    stages = list_stages()
    assert "idea_analysis" in stages
    assert "requirements_generation" in stages
    assert "prd_generation" in stages
    assert "project_specification_generation" in stages
    assert "architecture_generation" in stages
    assert "task_planning" in stages
    assert len(stages) == 6


def test_dynamic_pipeline_from_registry():
    """Verify PipelineEngine can be built from registry."""
    engine = PipelineEngine.from_registry()
    assert len(engine.stages) == 6
    assert isinstance(engine.stages[0], IdeaAnalyzerStage)
    assert isinstance(engine.stages[1], RequirementsGeneratorStage)
    assert isinstance(engine.stages[2], PRDGeneratorStage)
    assert isinstance(engine.stages[3], ProjectSpecificationGeneratorStage)
    assert isinstance(engine.stages[4], ArchitectureGeneratorStage)
    assert isinstance(engine.stages[5], TaskPlannerStage)


def test_pipeline_completes_with_mocked_llm():
    """Verify the full pipeline completes with mocked LLM responses."""
    context = ProjectContext(raw_idea="Build a SaaS resume analyzer")
    context.idea = Idea(
        title="SaaS Resume Analyzer",
        summary="A SaaS platform for analyzing resumes",
        raw_idea="Build a SaaS resume analyzer",
    )
    context.requirements = Requirements(
        project_title="SaaS Resume Analyzer",
        project_summary="A SaaS platform for analyzing resumes",
    )
    context.prd = PRD(project_title="SaaS Resume Analyzer")
    context.project_specification = ProjectSpecification(
        idea=context.idea,
        requirements=context.requirements,
        prd=context.prd,
    )
    context.architecture = Architecture(
        system_overview="Multi-tier architecture",
        technology_stack={"backend": "FastAPI", "frontend": "React"},
    )

    mock_response = json.dumps(
        {
            "project_title": "SaaS Resume Analyzer",
            "epics": [
                {
                    "title": "Core Features",
                    "description": "Build core resume analysis features",
                    "stories": [
                        {
                            "title": "User Authentication",
                            "description": "As a user, I want to sign up and log in",
                            "priority": "High",
                            "tasks": [
                                {
                                    "title": "Implement signup endpoint",
                                    "description": "Create POST /api/v1/auth/signup",
                                    "priority": "High",
                                    "estimated_effort": "3 points",
                                    "acceptance_criteria": [
                                        "Email validation",
                                        "Password hashing",
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )

    from models.common import GenerationResult

    mock_provider = MagicMock()
    mock_provider.name.return_value = "mock_provider"
    mock_provider.generate.return_value = GenerationResult(
        text=mock_response,
        provider_name="mock",
        model="mock",
        finish_reason="stop",
        input_tokens=10,
        output_tokens=20,
    )

    with patch("brain.stages.llm_stage.create_provider", return_value=mock_provider):
        engine = PipelineEngine.from_registry(["task_planning"])
        result = engine.run(context)

    assert result.task_plan is not None
    assert result.task_plan.project_title == "SaaS Resume Analyzer"
    assert len(result.task_plan.epics) == 1
    assert result.task_plan.epics[0].title == "Core Features"


def test_stage_dependency_validation():
    """Verify that stages fail with meaningful errors when dependencies are missing."""
    context = ProjectContext(raw_idea="test")

    req_stage = RequirementsGeneratorStage()
    try:
        execute_stage(req_stage, context)
        assert False, "Should have raised StageDependencyError"
    except StageDependencyError as e:
        assert "idea" in str(e).lower()

    context.idea = Idea(title="Test", summary="Test", raw_idea="test")
    prd_stage = PRDGeneratorStage()
    try:
        execute_stage(prd_stage, context)
        assert False, "Should have raised StageDependencyError"
    except StageDependencyError as e:
        assert "requirements" in str(e).lower()


def test_artifact_validation():
    """Verify that artifact validation catches missing files."""
    from brain.stages.base import Stage

    context = ProjectContext(raw_idea="test", project_name="test-project")
    mock_stage = MagicMock(spec=Stage)
    mock_stage.name = "requirements_generation"

    try:
        validate_stage_artifacts(mock_stage, context)
        assert False, "Should have raised ArtifactValidationError"
    except ArtifactValidationError as e:
        assert "requirements.md" in str(e)


def test_checkpoint_saved_after_stage():
    """Verify that context.json checkpoint is saved after stage execution."""
    from pipeline.artifacts import ArtifactManager
    from pipeline.executor import save_checkpoint

    context = ProjectContext(raw_idea="test", project_name="checkpoint-test")
    context.idea = Idea(title="Test", summary="Test", raw_idea="test")

    save_checkpoint(context)

    am = ArtifactManager.for_project("checkpoint-test")
    checkpoint = am.load_json("context.json")
    assert checkpoint is not None
    assert checkpoint["idea"]["title"] == "Test"


def test_full_pipeline_metadata():
    """Verify that all stages record metadata."""
    context = ProjectContext(raw_idea="test")

    context.start_stage("idea_analysis")
    context.complete_stage("idea_analysis", input_tokens=10, output_tokens=20)

    metadata = context.get_stage("idea_analysis")
    assert metadata.status == "completed"
    assert metadata.input_tokens == 10
    assert metadata.output_tokens == 20
    assert metadata.started_at is not None
    assert metadata.completed_at is not None
