"""
Application-layer service for Engineering Brain operations.

CLI commands call this service. The service calls brain stages.
This keeps the CLI independent of brain implementation details.
"""

from core.logging import get_logger
from models.project_context import ProjectContext
from pipeline.engine import PipelineEngine
from brain.idea.analyzer import IdeaAnalyzerStage

logger = get_logger(__name__)


def analyze_idea(idea_text: str) -> ProjectContext:
    """
    Analyze a raw user idea through the Idea Analyzer stage.

    Args:
        idea_text: The user's raw project idea.

    Returns:
        A ProjectContext with the idea field populated.

    Raises:
        ConfigurationError: If the AI provider is not configured.
        ProviderError: If analysis fails.
    """
    context = ProjectContext(raw_idea=idea_text)
    
    # We could also use the registry here if we wanted to be more dynamic
    engine = PipelineEngine(stages=[IdeaAnalyzerStage()])
    
    logger.info("Brain service: running analysis pipeline")
    return engine.run(context)
