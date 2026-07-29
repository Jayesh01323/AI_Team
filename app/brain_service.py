"""Application-layer service for Engineering Brain operations.

CLI commands call this service. The service calls brain stages.
This keeps the CLI independent of brain implementation details.
"""

from core.logging import get_logger
from models.project_context import ProjectContext
from pipeline.engine import PipelineEngine

logger = get_logger(__name__)


def analyze_idea(idea_text: str) -> ProjectContext:
    context = ProjectContext(raw_idea=idea_text)
    engine = PipelineEngine.from_registry(["idea_analysis"])
    logger.info("Brain service: running analysis pipeline")
    return engine.run(context)


def analyze_and_generate_requirements(idea_text: str) -> ProjectContext:
    context = ProjectContext(raw_idea=idea_text)
    engine = PipelineEngine.from_registry(["idea_analysis", "requirements_generation"])
    logger.info("Brain service: running analysis + requirements pipeline")
    return engine.run(context)


def run_full_pipeline(idea_text: str) -> ProjectContext:
    """
    Run the full Engineering Brain pipeline using the dynamic registry.

    Stages are executed in registration order:
        1. Idea Analysis
        2. Requirements Generation
        3. PRD Generation
        4. ProjectSpecification Generation
        5. Architecture Generation
        6. Task Planning

    Produces requirements.md, PRD.md, prd.json, project_specification.json,
    architecture.json, ARCHITECTURE.md, task_plan.json, TASKS.md, and
    context.json (checkpoint) on disk.
    """
    context = ProjectContext(raw_idea=idea_text)
    engine = PipelineEngine.from_registry()
    logger.info("Brain service: running full pipeline from registry")
    return engine.run(context)
