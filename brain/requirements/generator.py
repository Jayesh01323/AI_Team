"""
Requirements Generator Stage — converts an analyzed Idea into a structured Requirements model.

This is the second Engineering Brain stage. It inherits from LLMStage
and produces both a domain model and a Markdown file.
"""

from typing import Any

from brain.json_utils import extract_json_from_response
from brain.stages.llm_stage import LLMStage
from models.project_context import ProjectContext
from models.requirements import Requirements
from pipeline.artifacts import ArtifactManager
from pipeline.registry import register_stage


@register_stage
class RequirementsGeneratorStage(LLMStage):
    """Stage that generates structured requirements from an analyzed idea."""

    @property
    def name(self) -> str:
        return "requirements_generation"

    @property
    def prompt_template_name(self) -> str:
        return "requirements"

    def get_prompt_kwargs(self, context: ProjectContext) -> dict[str, Any]:
        if not context.idea:
            raise ValueError("No idea in context. Run IdeaAnalyzerStage first.")

        idea = context.idea
        return {
            "project_title": idea.title,
            "project_summary": idea.summary,
            "target_users": ", ".join(idea.target_users)
            if idea.target_users
            else "Not specified",
            "functional_requirements": ", ".join(idea.functional_requirements)
            if idea.functional_requirements
            else "None identified yet",
            "non_functional_requirements": ", ".join(idea.non_functional_requirements)
            if idea.non_functional_requirements
            else "None identified yet",
        }

    def parse_response(
        self, response_text: str, context: ProjectContext
    ) -> Requirements:
        """Parse the JSON response into a Requirements model."""
        data = extract_json_from_response(response_text)

        title = data.get(
            "project_title", context.idea.title if context.idea else "Untitled"
        )

        return Requirements(
            project_title=title,
            project_summary=data.get("project_summary", ""),
            functional_requirements=data.get("functional_requirements", []),
            non_functional_requirements=data.get("non_functional_requirements", []),
            user_stories=data.get("user_stories", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            must_have=data.get("must_have", []),
            should_have=data.get("should_have", []),
            could_have=data.get("could_have", []),
            external_dependencies=data.get("external_dependencies", []),
            in_scope=data.get("in_scope", []),
            out_of_scope=data.get("out_of_scope", []),
        )

    def update_context(
        self, context: ProjectContext, parsed_output: Requirements
    ) -> ProjectContext:
        """Update context with Requirements model and save via ArtifactManager."""
        context.requirements = parsed_output

        # Use ArtifactManager instead of writing files directly
        am = ArtifactManager.for_project(context.project_name)
        am.save_markdown("requirements.md", parsed_output.to_markdown())

        return context
