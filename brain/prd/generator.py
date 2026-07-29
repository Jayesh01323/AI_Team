"""
PRD Generator Stage — converts Idea + Requirements into a structured PRD model.

This is the third Engineering Brain stage. It inherits from LLMStage
and produces both a domain model, PRD.md, and prd.json via ArtifactManager.
"""

from typing import Any

from brain.json_utils import extract_json_from_response
from brain.stages.llm_stage import LLMStage
from models.prd import PRD
from models.project_context import ProjectContext
from pipeline.artifacts import ArtifactManager
from pipeline.registry import register_stage


@register_stage
class PRDGeneratorStage(LLMStage):
    """Stage that generates a Product Requirements Document from Idea and Requirements."""

    @property
    def name(self) -> str:
        return "prd_generation"

    @property
    def prompt_template_name(self) -> str:
        return "prd"

    def get_prompt_kwargs(self, context: ProjectContext) -> dict[str, Any]:
        if not context.idea:
            raise ValueError("No idea in context. Run IdeaAnalyzerStage first.")
        if not context.requirements:
            raise ValueError(
                "No requirements in context. Run RequirementsGeneratorStage first."
            )

        req = context.requirements
        return {
            "project_title": req.project_title,
            "project_summary": req.project_summary,
            "functional_requirements": "; ".join(req.functional_requirements)
            if req.functional_requirements
            else "None",
            "non_functional_requirements": "; ".join(req.non_functional_requirements)
            if req.non_functional_requirements
            else "None",
            "user_stories": "; ".join(req.user_stories) if req.user_stories else "None",
            "acceptance_criteria": "; ".join(req.acceptance_criteria)
            if req.acceptance_criteria
            else "None",
            "must_have": "; ".join(req.must_have) if req.must_have else "None",
            "external_dependencies": "; ".join(req.external_dependencies)
            if req.external_dependencies
            else "None",
        }

    def parse_response(self, response_text: str, context: ProjectContext) -> PRD:
        """Parse the JSON response into a PRD model."""
        data = extract_json_from_response(response_text)
        title = data.get(
            "project_title",
            context.requirements.project_title if context.requirements else "Untitled",
        )

        return PRD(
            project_title=title,
            problem_statement=data.get("problem_statement", ""),
            project_vision=data.get("project_vision", ""),
            target_audience=data.get("target_audience", []),
            user_personas=data.get("user_personas", []),
            user_journeys=data.get("user_journeys", []),
            features=data.get("features", []),
            success_metrics=data.get("success_metrics", []),
            kpis=data.get("kpis", []),
            mvp_scope=data.get("mvp_scope", []),
            future_scope=data.get("future_scope", []),
            competitors=data.get("competitors", []),
            differentiation=data.get("differentiation", []),
            estimated_timeline=data.get("estimated_timeline", ""),
        )

    def update_context(
        self, context: ProjectContext, parsed_output: PRD
    ) -> ProjectContext:
        """Update context with PRD model and save artifacts via ArtifactManager."""
        context.prd = parsed_output

        am = ArtifactManager.for_project(context.project_name)
        am.save_markdown("PRD.md", parsed_output.to_markdown())
        am.save_json("prd.json", parsed_output.to_dict())

        return context
