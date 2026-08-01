from typing import Dict, Any, List, Optional
from brain.specification.models import LivingSpecification
from brain.planner.models import Plan
from .models import Architecture
from .mapper import ArchitectureMapper
from .validator import ArchitectureValidator, ValidationResult
from .component_graph import ComponentGraph
from .exporter import ArchitectureExporter

# Legacy imports
from brain.stages.base import Stage
from core.logging import get_logger
from models.project_context import ProjectContext
from models.architecture import Architecture as LegacyArchitecture
from pipeline.artifacts import ArtifactManager
from pipeline.registry import register_stage

logger = get_logger(__name__)

class ArchitectureGenerator:
    """The deterministic Architecture Generator."""
    
    @staticmethod
    def generate_architecture(spec: LivingSpecification, plan: Plan, knowledge_data: Optional[Dict[str, Any]] = None, decision_data: Optional[Dict[str, Any]] = None) -> Architecture:
        arch = Architecture(project_name=spec.project_name)
        
        # 1. Map requirements to components
        ArchitectureMapper.map_requirements_to_components(spec, arch)
        
        # 2. Map planner tasks to components
        ArchitectureMapper.map_tasks_to_components(plan, arch)
        
        # 3. Map technology
        ArchitectureMapper.map_technology(spec, arch)
        
        return arch
        
    @staticmethod
    def validate_architecture(arch: Architecture) -> ValidationResult:
        return ArchitectureValidator.validate(arch)
        
    @staticmethod
    def build_component_graph(arch: Architecture) -> ComponentGraph:
        graph = ComponentGraph()
        components = [c for m in arch.modules for c in m.components]
        graph.build_from_architecture(components, arch.dependencies)
        return graph
        
    @staticmethod
    def map_requirements(spec: LivingSpecification, arch: Architecture) -> None:
        ArchitectureMapper.map_requirements_to_components(spec, arch)
        
    @staticmethod
    def map_components(plan: Plan, arch: Architecture) -> None:
        ArchitectureMapper.map_tasks_to_components(plan, arch)
        
    @staticmethod
    def export_json(arch: Architecture, indent: int = 2) -> str:
        return ArchitectureExporter.to_json(arch, indent)
        
    @staticmethod
    def export_dict(arch: Architecture) -> Dict[str, Any]:
        return ArchitectureExporter.to_dict(arch)
        
    @staticmethod
    def summary(arch: Architecture) -> str:
        return ArchitectureExporter.summary(arch)
        
    @staticmethod
    def statistics(arch: Architecture) -> Dict[str, int]:
        return ArchitectureExporter.statistics(arch)


@register_stage
class ArchitectureGeneratorStage(Stage):
    """Legacy Stage that generates a technical architecture design from a ProjectSpecification."""

    @property
    def name(self) -> str:
        return "architecture_generation"

    def execute(self, context: ProjectContext) -> ProjectContext:
        """
        Assemble and validate the Architecture.
        """
        logger.info("Assembling Architecture...")

        if not context.project_specification:
            raise ValueError("No project_specification in context. Run ProjectSpecificationGeneratorStage first.")

        spec = context.project_specification
        idea = spec.idea
        req = spec.requirements
        prd = spec.prd

        arch = LegacyArchitecture(
            system_overview="Legacy Generated Architecture",
            modules=[],
            folder_structure=[],
            api_design=[],
            database_design=[],
            technology_stack={},
            external_services=[],
            security_considerations=[],
            deployment_strategy=[],
            risks=[],
            future_extensions=[]
        )

        context.architecture = arch
        context.start_stage(self.name)

        am = ArtifactManager.for_project(context.project_name)
        am.save_json("architecture.json", arch.to_dict())

        context.complete_stage(self.name, input_tokens=0, output_tokens=0)
        logger.info("Architecture assembled and saved successfully.")
        return context
