"""
Stage executor.

Handles the execution logic for a single stage, including
error handling and logging.
"""

from brain.stages.base import Stage
from models.project_context import ProjectContext
from core.logging import get_logger

logger = get_logger(__name__)


def execute_stage(stage: Stage, context: ProjectContext) -> ProjectContext:
    """
    Execute a single stage on the given context.

    Args:
        stage: The stage instance to execute.
        context: The current ProjectContext.

    Returns:
        The updated ProjectContext.
    """
    if not stage.should_execute(context):
        logger.info(f"Skipping stage: {stage.name}")
        return context

    logger.info(f"Executing stage: {stage.name}")
    try:
        context = stage.execute(context)
        return context
    except Exception as e:
        logger.error(f"Stage '{stage.name}' failed: {str(e)}")
        context.fail_stage(stage.name, str(e))
        raise
