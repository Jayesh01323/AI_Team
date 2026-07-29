"""
Idea Analyzer Stage — converts a raw user idea into a structured Idea model.

This is the first Engineering Brain stage. It inherits from LLMStage
to handle common LLM orchestration.
"""

from typing import Any

from brain.json_utils import extract_json_from_response
from brain.stages.llm_stage import LLMStage
from models.idea import Idea
from models.project_context import ProjectContext
from pipeline.registry import register_stage


@register_stage
class IdeaAnalyzerStage(LLMStage):
    """Stage that analyzes a raw idea and produces an Idea model."""

    @property
    def name(self) -> str:
        return "idea_analysis"

    @property
    def prompt_template_name(self) -> str:
        return "idea_analysis"

    def get_prompt_kwargs(self, context: ProjectContext) -> dict[str, Any]:
        if not context.raw_idea:
            raise ValueError("No raw_idea in context")
        return {"idea_text": context.raw_idea}

    def parse_response(self, response_text: str, context: ProjectContext) -> Idea:
        """Parse the JSON response into an Idea model."""
        data = extract_json_from_response(response_text)

        # Populate Idea model
        title = data.get("title", "")
        if not title:
            title = context.raw_idea[:64]

        return Idea(
            title=title,
            summary=data.get("summary", ""),
            target_users=data.get("target_users", []),
            functional_requirements=data.get("functional_requirements", []),
            non_functional_requirements=data.get("non_functional_requirements", []),
            assumptions=data.get("assumptions", []),
            constraints=data.get("constraints", []),
            risks=data.get("risks", []),
            unknowns=data.get("unknowns", []),
            clarification_questions=data.get("clarification_questions", []),
            raw_idea=context.raw_idea,
        )

    def update_context(
        self, context: ProjectContext, parsed_output: Idea
    ) -> ProjectContext:
        context.idea = parsed_output
        return context


def analyze_idea(idea_text: str) -> ProjectContext:
    """
    Convenience function to run idea analysis.

    Creates context and executes the IdeaAnalyzerStage.
    """
    context = ProjectContext(raw_idea=idea_text)
    stage = IdeaAnalyzerStage()
    return stage.execute(context)
