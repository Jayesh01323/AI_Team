"""
Stage executor.

Handles the execution logic for a single stage, including
validation, error handling, checkpointing, and logging.
"""

from brain.stages.base import Stage
from core.logging import get_logger
from models.project_context import ProjectContext
from pipeline.artifacts import ArtifactManager

logger = get_logger(__name__)


class StageDependencyError(Exception):
    """Raised when a stage's dependencies are not met."""


class ArtifactValidationError(Exception):
    """Raised when required artifacts are missing after stage execution."""


def validate_stage_inputs(stage: Stage, context: ProjectContext) -> None:
    """
    Validate that the stage's required inputs exist in the context.

    Args:
        stage: The stage to validate.
        context: The current ProjectContext.

    Raises:
        StageDependencyError: If required inputs are missing.
    """
    stage_name = stage.name

    if stage_name == "idea_analysis":
        if not context.raw_idea:
            raise StageDependencyError("IdeaAnalysis requires raw_idea in context")

    elif stage_name == "requirements_generation":
        if not context.idea:
            raise StageDependencyError(
                "RequirementsGeneration requires idea in context. Run IdeaAnalyzerStage first."
            )

    elif stage_name == "prd_generation":
        if not context.idea:
            raise StageDependencyError(
                "PRDGeneration requires idea in context. Run IdeaAnalyzerStage first."
            )
        if not context.requirements:
            raise StageDependencyError(
                "PRDGeneration requires requirements in context. Run RequirementsGeneratorStage first."
            )

    elif stage_name == "project_specification_generation":
        if not context.idea:
            raise StageDependencyError(
                "ProjectSpecificationGeneration requires idea in context."
            )
        if not context.requirements:
            raise StageDependencyError(
                "ProjectSpecificationGeneration requires requirements in context."
            )
        if not context.prd:
            raise StageDependencyError(
                "ProjectSpecificationGeneration requires prd in context."
            )

    elif stage_name == "architecture_generation":
        if not context.project_specification:
            raise StageDependencyError(
                "ArchitectureGeneration requires project_specification in context. Run ProjectSpecificationGeneratorStage first."
            )

    elif stage_name == "task_planning":
        if not context.project_specification:
            raise StageDependencyError(
                "TaskPlanning requires project_specification in context."
            )
        if not context.architecture:
            raise StageDependencyError(
                "TaskPlanning requires architecture in context. Run ArchitectureGeneratorStage first."
            )


def validate_stage_artifacts(stage: Stage, context: ProjectContext) -> None:
    """
    Validate that the stage produced its expected artifacts.

    Args:
        stage: The stage that just executed.
        context: The current ProjectContext.

    Raises:
        ArtifactValidationError: If expected artifacts are missing.
    """
    stage_name = stage.name
    project_name = context.project_name

    if not project_name:
        return

    am = ArtifactManager.for_project(project_name)

    if stage_name == "requirements_generation":
        if not am.load_markdown("requirements.md"):
            raise ArtifactValidationError(
                "requirements.md was not created by RequirementsGeneratorStage"
            )

    elif stage_name == "prd_generation":
        if not am.load_markdown("PRD.md"):
            raise ArtifactValidationError("PRD.md was not created by PRDGeneratorStage")
        if not am.load_json("prd.json"):
            raise ArtifactValidationError(
                "prd.json was not created by PRDGeneratorStage"
            )

    elif stage_name == "project_specification_generation":
        if not am.load_json("project_specification.json"):
            raise ArtifactValidationError(
                "project_specification.json was not created by ProjectSpecificationGeneratorStage"
            )

    elif stage_name == "architecture_generation":
        if not am.load_markdown("ARCHITECTURE.md"):
            raise ArtifactValidationError(
                "ARCHITECTURE.md was not created by ArchitectureGeneratorStage"
            )
        if not am.load_json("architecture.json"):
            raise ArtifactValidationError(
                "architecture.json was not created by ArchitectureGeneratorStage"
            )

    elif stage_name == "task_planning":
        if not am.load_markdown("TASKS.md"):
            raise ArtifactValidationError(
                "TASKS.md was not created by TaskPlannerStage"
            )
        if not am.load_json("task_plan.json"):
            raise ArtifactValidationError(
                "task_plan.json was not created by TaskPlannerStage"
            )


def save_checkpoint(context: ProjectContext) -> None:
    """
    Save a checkpoint of the current ProjectContext.

    Args:
        context: The current ProjectContext to save.
    """
    if not context.project_name:
        return

    am = ArtifactManager.for_project(context.project_name)
    am.save_json("context.json", context.to_dict())
    logger.info("Checkpoint saved: context.json")


def execute_stage(stage: Stage, context: ProjectContext) -> ProjectContext:
    """
    Execute a single stage on the given context.

    Args:
        stage: The stage instance to execute.
        context: The current ProjectContext.

    Returns:
        The updated ProjectContext.

    Raises:
        StageDependencyError: If stage dependencies are not met.
        ArtifactValidationError: If stage fails to produce expected artifacts.
        ProviderError: If the provider fails.
    """
    if not stage.should_execute(context):
        logger.info(f"Skipping stage: {stage.name}")
        return context

    # Validate inputs before execution
    validate_stage_inputs(stage, context)

    logger.info(f"Executing stage: {stage.name}")
    try:
        context = stage.execute(context)
    except Exception as e:
        logger.error(f"Stage '{stage.name}' failed: {e!s}")
        context.fail_stage(stage.name, str(e))
        raise

    # Validate artifacts after execution
    validate_stage_artifacts(stage, context)

    # Save checkpoint after successful stage completion
    save_checkpoint(context)

    return context
