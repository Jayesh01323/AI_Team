"""
Idea Analyzer Stage — converts a raw user idea into a structured Idea model.

This is the first Engineering Brain stage. It inherits from LLMStage
to handle common LLM orchestration.
"""

import json
import re
from typing import Any

from brain.stages.llm_stage import LLMStage
from core.exceptions import ProviderError
from core.logging import get_logger
from models.idea import Idea
from models.project_context import ProjectContext
from pipeline.registry import register_stage

logger = get_logger(__name__)


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
        data = self._extract_json(response_text)

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

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from response text, handling markdown fences."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, trying regex fallback")
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            raise ProviderError(f"Provider returned invalid JSON: {text[:200]}")


def analyze_idea(idea_text: str) -> ProjectContext:
    """
    Convenience function to run idea analysis.

    Creates context and executes the IdeaAnalyzerStage.
    """
    context = ProjectContext(raw_idea=idea_text)
    stage = IdeaAnalyzerStage()
    return stage.execute(context)
