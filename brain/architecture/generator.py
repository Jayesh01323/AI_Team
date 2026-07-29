"""
Architecture Generator Stage — converts a ProjectSpecification into a structured Architecture model.

This is the fifth Engineering Brain stage. It inherits from LLMStage
and produces system architecture designs, architecture.json, and ARCHITECTURE.md via ArtifactManager.
"""

from typing import Any

from brain.json_utils import extract_json_from_response
from brain.stages.llm_stage import LLMStage
from models.architecture import Architecture
from models.project_context import ProjectContext
from pipeline.artifacts import ArtifactManager
from pipeline.registry import register_stage


@register_stage
class ArchitectureGeneratorStage(LLMStage):
    """Stage that generates a comprehensive technical architecture design from a ProjectSpecification."""

    @property
    def name(self) -> str:
        return "architecture_generation"

    @property
    def prompt_template_name(self) -> str:
        return "architecture"

    def get_prompt_kwargs(self, context: ProjectContext) -> dict[str, Any]:
        if not context.project_specification:
            raise ValueError(
                "No project_specification in context. Run ProjectSpecificationGeneratorStage first."
            )

        spec = context.project_specification
        idea = spec.idea
        req = spec.requirements
        prd = spec.prd

        return {
            "project_title": idea.title,
            "project_summary": idea.summary,
            "functional_requirements": "; ".join(req.functional_requirements)
            if req.functional_requirements
            else "None",
            "non_functional_requirements": "; ".join(req.non_functional_requirements)
            if req.non_functional_requirements
            else "None",
            "prd_features": "; ".join(prd.features) if prd.features else "None",
            "mvp_scope": "; ".join(prd.mvp_scope) if prd.mvp_scope else "None",
            "external_dependencies": "; ".join(prd.competitors)
            if prd.competitors
            else "None",
        }

    def parse_response(
        self, response_text: str, context: ProjectContext
    ) -> Architecture:
        """Parse the JSON response into an Architecture model."""
        data = extract_json_from_response(response_text)

        return Architecture(
            system_overview=data.get("system_overview", ""),
            modules=data.get("modules", []),
            folder_structure=data.get("folder_structure", []),
            api_design=data.get("api_design", []),
            database_design=data.get("database_design", []),
            technology_stack=data.get("technology_stack", {}),
            external_services=data.get("external_services", []),
            security_considerations=data.get("security_considerations", []),
            deployment_strategy=data.get("deployment_strategy", []),
            risks=data.get("risks", []),
            future_extensions=data.get("future_extensions", []),
        )

    def update_context(
        self, context: ProjectContext, parsed_output: Architecture
    ) -> ProjectContext:
        """Update context with Architecture model and save artifacts via ArtifactManager."""
        context.architecture = parsed_output

        # Save artifacts using ArtifactManager
        am = ArtifactManager.for_project(context.project_name)
        am.save_markdown("ARCHITECTURE.md", parsed_output.to_markdown())
        am.save_json("architecture.json", parsed_output.to_dict())

        return context
