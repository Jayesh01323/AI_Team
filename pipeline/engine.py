"""
Pipeline Engine — LLM-Powered Analysis Pipeline (LEGACY)

Manages the sequential execution of engineering stages using AI providers.
This is the LEGACY pipeline for transforming raw ideas into structured models.

ARCHITECTURE BOUNDARY:
-----------------------
This is the LLM-POWERED ANALYSIS path, distinct from:

  - brain/project_generator/pipeline.py (ProjectGenerationPipeline): Deterministic generation
      Purpose: Generate actual code from approved blueprints
      Stages: Template Resolution → Code Generation → Assembly → Validation → Repair → Export
      Input: ProjectBlueprint
      Output: Generated project files on disk

  - pipeline/engine.py (PipelineEngine): LLM-powered analysis pipeline [THIS FILE]
      Purpose: Transform raw ideas into structured models using AI
      Stages: Idea Analysis → Requirements → PRD → Architecture → Task Planning
      Input: Raw idea text
      Output: ProjectContext with structured domain models

DO NOT mix these two pipelines. They serve different phases of the workflow.
For new code, prefer the deterministic generators in brain.specification, 
brain.architecture, and brain.planner over these legacy stages.
"""

from brain.stages.base import Stage
from core.logging import get_logger
from models.project_context import ProjectContext
from pipeline.executor import execute_stage
from pipeline.registry import get_stage_class, list_stages

logger = get_logger(__name__)


class PipelineEngine:
    """Engine to execute a sequence of stages."""

    def __init__(self, stages: list[Stage]):
        self.stages = stages

    def run(self, context: ProjectContext) -> ProjectContext:
        """
        Run all stages in sequence.

        Args:
            context: Initial ProjectContext.

        Returns:
            Final ProjectContext after all stages have executed.
        """
        logger.info(f"Starting pipeline with {len(self.stages)} stages")
        for stage in self.stages:
            context = execute_stage(stage, context)
        logger.info("Pipeline execution complete")
        return context

    @classmethod
    def from_registry(cls, stage_names: list[str] | None = None) -> "PipelineEngine":
        """
        Create a PipelineEngine from the stage registry.

        Args:
            stage_names: Optional list of stage names to include.
                        If None, includes all registered stages in order.

        Returns:
            A PipelineEngine instance with the requested stages, sorted by execution order.
        """
        if stage_names is None:
            stage_names = list_stages()

        # Sort stages by their registered execution order
        stages_with_order = []
        for name in stage_names:
            stage_class = get_stage_class(name)
            # Get order from registry
            from pipeline.registry import _REGISTRY
            _, order = _REGISTRY[name]
            stages_with_order.append((order, stage_class))
        
        # Sort by order and instantiate
        stages_with_order.sort(key=lambda x: x[0])
        stages = [stage_class() for _, stage_class in stages_with_order]

        return cls(stages)
