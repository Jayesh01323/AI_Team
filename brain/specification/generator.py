from typing import Dict, Any, Tuple
from .models import LivingSpecification
from .updater import update_specification
from .validator import validate_specification, ValidationResult
from .merger import merge_specifications
from .exporter import export_to_dict, export_to_json, generate_summary, generate_statistics

# Legacy pipeline imports
from brain.stages.base import Stage
from core.logging import get_logger
from models.project_context import ProjectContext
from models.project_specification import ProjectSpecification as LegacyProjectSpecification
from pipeline.artifacts import ArtifactManager
from pipeline.registry import register_stage

logger = get_logger(__name__)

class LivingSpecificationGenerator:
    """The deterministic Living Specification Generator."""
    
    @staticmethod
    def generate(knowledge_data: Dict[str, Any] = None, 
                 intent_data: Dict[str, Any] = None, 
                 decision_data: Dict[str, Any] = None) -> LivingSpecification:
        """Generates an initial Living Specification from the outputs of the 
        Knowledge Model, Intent Engine, and Decision Engine."""
        
        knowledge_data = knowledge_data or {}
        intent_data = intent_data or {}
        decision_data = decision_data or {}
        
        spec = LivingSpecification()
        
        # Extract from knowledge
        if "project_name" in knowledge_data:
            spec.project_name = knowledge_data["project_name"]
        if "vision" in knowledge_data:
            spec.vision = knowledge_data["vision"]
        if "mission" in knowledge_data:
            spec.mission = knowledge_data["mission"]
        if "problem_statement" in knowledge_data:
            spec.problem_statement = knowledge_data["problem_statement"]
        if "target_users" in knowledge_data:
            spec.target_users = list(knowledge_data["target_users"])
            
        # Extract from intent
        if "goals" in intent_data:
            spec.goals = list(intent_data["goals"])
        if "success_criteria" in intent_data:
            spec.success_criteria = list(intent_data["success_criteria"])
            
        # Extract from decisions
        if "accepted_decisions" in decision_data:
            spec.accepted_decisions = list(decision_data["accepted_decisions"])
        if "rejected_decisions" in decision_data:
            spec.rejected_decisions = list(decision_data["rejected_decisions"])
        if "superseded_decisions" in decision_data:
            spec.superseded_decisions = list(decision_data["superseded_decisions"])
            
        return spec
    
    @staticmethod
    def update(current: LivingSpecification, update: LivingSpecification) -> Tuple[LivingSpecification, ValidationResult]:
        return update_specification(current, update)
        
    @staticmethod
    def validate(spec: LivingSpecification) -> ValidationResult:
        return validate_specification(spec)
        
    @staticmethod
    def merge(current: LivingSpecification, update: LivingSpecification) -> LivingSpecification:
        return merge_specifications(current, update)
        
    @staticmethod
    def export_json(spec: LivingSpecification, indent: int = 2) -> str:
        return export_to_json(spec, indent)
        
    @staticmethod
    def export_dict(spec: LivingSpecification) -> Dict[str, Any]:
        return export_to_dict(spec)
        
    @staticmethod
    def summary(spec: LivingSpecification) -> str:
        return generate_summary(spec)
        
    @staticmethod
    def statistics(spec: LivingSpecification) -> Dict[str, int]:
        return generate_statistics(spec)


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
        spec = LegacyProjectSpecification(
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
