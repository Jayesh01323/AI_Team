"""
Pipeline engine.

Manages the sequential execution of engineering stages.
"""

from typing import List
from brain.stages.base import Stage
from models.project_context import ProjectContext
from pipeline.executor import execute_stage
from core.logging import get_logger

logger = get_logger(__name__)


class PipelineEngine:
    """Engine to execute a sequence of stages."""

    def __init__(self, stages: List[Stage]):
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
