"""
Legacy ProjectSpecificationGeneratorStage.

This is the LEGACY LLM-based stage for assembling ProjectSpecification.
It is kept for backwards compatibility with the legacy pipeline system.

For new code, use LivingSpecificationGenerator (deterministic) instead.
"""

from brain.stages.base import Stage
from core.logging import get_logger
from models.project_context import ProjectContext
from models.project_specification import ProjectSpecification
from pipeline.artifacts import ArtifactManager
from pipeline.registry import register_stage

logger = get_logger(__name__)


@register_stage
class ProjectSpecificationGeneratorStage(Stage):
    """Legacy Stage that assembles a validated ProjectSpecification from preceding outputs."""

    @property
    def name(self) -> str:
        return "project_specification_generation"

    def execute(self, context: ProjectContext) -> ProjectContext:
        """
        Assemble and validate the ProjectSpecification.
        """
        logger.info("Assembling ProjectSpecification...")

        # 1. Validation
        if not context.idea:
            raise ValueError("No idea in context. Run IdeaAnalyzerStage first.")
        if not context.requirements:
            raise ValueError(
                "No requirements in context. Run RequirementsGeneratorStage first."
            )
        if not context.prd:
            raise ValueError("No PRD in context. Run PRDGeneratorStage first.")

        # 2. Assemble ProjectSpecification
        spec = ProjectSpecification(
            idea=context.idea,
            requirements=context.requirements,
            prd=context.prd,
        )

        context.project_specification = spec

        # Start/Complete Stage Metadata
        context.start_stage(self.name)

        # 3. Save artifacts using ArtifactManager
        am = ArtifactManager.for_project(context.project_name)
        am.save_json("project_specification.json", spec.to_dict())

        context.complete_stage(self.name, input_tokens=0, output_tokens=0)

        logger.info("ProjectSpecification assembled and saved successfully.")
        return context