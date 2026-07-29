"""
Task Planner Stage — converts Architecture + ProjectSpecification into a structured TaskPlan model.

This is the sixth Engineering Brain stage. It inherits from LLMStage
and produces a comprehensive implementation roadmap, task_plan.json, and TASKS.md via ArtifactManager.
"""

from typing import Any

from brain.json_utils import extract_json_from_response
from brain.stages.llm_stage import LLMStage
from models.project_context import ProjectContext
from models.task_plan import Epic, Story, Task, TaskPlan
from pipeline.artifacts import ArtifactManager
from pipeline.registry import register_stage


@register_stage
class TaskPlannerStage(LLMStage):
    """Stage that generates a comprehensive implementation roadmap from Architecture and ProjectSpecification."""

    @property
    def name(self) -> str:
        return "task_planning"

    @property
    def prompt_template_name(self) -> str:
        return "task_planner"

    def get_prompt_kwargs(self, context: ProjectContext) -> dict[str, Any]:
        if not context.project_specification:
            raise ValueError(
                "No project_specification in context. Run ProjectSpecificationGeneratorStage first."
            )
        if not context.architecture:
            raise ValueError(
                "No architecture in context. Run ArchitectureGeneratorStage first."
            )

        spec = context.project_specification
        arch = context.architecture
        idea = spec.idea
        req = spec.requirements

        return {
            "project_title": idea.title,
            "project_summary": idea.summary,
            "functional_requirements": "; ".join(req.functional_requirements)
            if req.functional_requirements
            else "None",
            "non_functional_requirements": "; ".join(req.non_functional_requirements)
            if req.non_functional_requirements
            else "None",
            "system_overview": arch.system_overview,
            "modules": "; ".join(arch.modules) if arch.modules else "None",
            "technology_stack": "; ".join(
                [f"{k}: {v}" for k, v in arch.technology_stack.items()]
            )
            if arch.technology_stack
            else "None",
            "folder_structure": "; ".join(arch.folder_structure)
            if arch.folder_structure
            else "None",
            "api_design": "; ".join(arch.api_design) if arch.api_design else "None",
            "database_design": "; ".join(arch.database_design)
            if arch.database_design
            else "None",
        }

    def parse_response(self, response_text: str, context: ProjectContext) -> TaskPlan:
        """Parse the JSON response into a TaskPlan model."""
        data = extract_json_from_response(response_text)

        title = data.get(
            "project_title",
            context.project_specification.idea.title
            if context.project_specification
            else "Untitled",
        )

        # Parse epics, stories, and tasks from nested JSON
        epics = []
        for epic_data in data.get("epics", []):
            stories = []
            for story_data in epic_data.get("stories", []):
                tasks = []
                for task_data in story_data.get("tasks", []):
                    task = Task(
                        title=task_data.get("title", ""),
                        description=task_data.get("description", ""),
                        priority=task_data.get("priority", "Medium"),
                        dependencies=task_data.get("dependencies", []),
                        estimated_effort=task_data.get("estimated_effort", ""),
                        acceptance_criteria=task_data.get("acceptance_criteria", []),
                    )
                    tasks.append(task)

                story = Story(
                    title=story_data.get("title", ""),
                    description=story_data.get("description", ""),
                    priority=story_data.get("priority", "Medium"),
                    tasks=tasks,
                )
                stories.append(story)

            epic = Epic(
                title=epic_data.get("title", ""),
                description=epic_data.get("description", ""),
                stories=stories,
            )
            epics.append(epic)

        return TaskPlan(
            project_title=title,
            epics=epics,
        )

    def update_context(
        self, context: ProjectContext, parsed_output: TaskPlan
    ) -> ProjectContext:
        """Update context with TaskPlan model and save artifacts via ArtifactManager."""
        context.task_plan = parsed_output

        # Save artifacts using ArtifactManager
        am = ArtifactManager.for_project(context.project_name)
        am.save_markdown("TASKS.md", parsed_output.to_markdown())
        am.save_json("task_plan.json", parsed_output.to_dict())

        return context
