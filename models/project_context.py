"""
ProjectContext — progressively accumulates all Engineering Brain stage outputs.

Each stage (Idea Analysis, Requirements, PRD, Architecture, etc.) reads the
current context and writes its output back. The context grows as stages complete.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from models.architecture import Architecture
from models.idea import Idea
from models.prd import PRD
from models.project_specification import ProjectSpecification
from models.requirements import Requirements
from models.task_plan import TaskPlan


@dataclass
class StageMetadata:
    """Metadata about a single stage execution."""

    stage_name: str
    status: str = "pending"  # pending, running, completed, failed
    started_at: str | None = None
    completed_at: str | None = None
    provider_name: str | None = None
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    error: str | None = None


@dataclass
class ProjectContext:
    """
    Accumulates all Engineering Brain stage outputs.

    Start with raw_idea. Each stage adds its structured output.
    Stages read previous outputs for context.
    """

    # Original input
    raw_idea: str = ""

    # Stage outputs (populated progressively)
    idea: Idea | None = None
    requirements: Requirements | None = None
    prd: PRD | None = None
    project_specification: ProjectSpecification | None = None
    architecture: Architecture | None = None
    task_plan: TaskPlan | None = None
    # Future stages will add: tech_stack

    # Stage execution metadata
    metadata: dict[str, StageMetadata] = field(default_factory=dict)

    # Project identification
    project_name: str = ""
    created_at: str = ""
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        if not self.project_name and self.raw_idea:
            import re

            name = self.raw_idea.lower().strip()
            name = re.sub(r"[^a-z0-9]+", "-", name)
            name = name.strip("-")
            self.project_name = name[:64]

    def get_stage(self, name: str) -> StageMetadata:
        """Get metadata for a stage, creating it if it doesn't exist."""
        if name not in self.metadata:
            self.metadata[name] = StageMetadata(stage_name=name)
        return self.metadata[name]

    def start_stage(
        self, name: str, provider_name: str | None = None, model: str | None = None
    ) -> None:
        """Mark a stage as running."""
        stage = self.get_stage(name)
        stage.status = "running"
        stage.started_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        if provider_name:
            stage.provider_name = provider_name
        if model:
            stage.model = model

    def complete_stage(
        self,
        name: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        """Mark a stage as completed."""
        stage = self.get_stage(name)
        stage.status = "completed"
        stage.completed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        if input_tokens is not None:
            stage.input_tokens = input_tokens
        if output_tokens is not None:
            stage.output_tokens = output_tokens

    def fail_stage(self, name: str, error: str) -> None:
        """Mark a stage as failed."""
        stage = self.get_stage(name)
        stage.status = "failed"
        stage.completed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        stage.error = error

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "project_name": self.project_name,
            "raw_idea": self.raw_idea,
            "created_at": self.created_at,
            "idea": self.idea.to_dict() if self.idea else None,
            "requirements": self.requirements.to_dict() if self.requirements else None,
            "prd": self.prd.to_dict() if self.prd else None,
            "project_specification": self.project_specification.to_dict()
            if self.project_specification
            else None,
            "architecture": self.architecture.to_dict() if self.architecture else None,
            "task_plan": self.task_plan.to_dict() if self.task_plan else None,
            "metadata": {
                name: {
                    "stage": m.stage_name,
                    "status": m.status,
                    "started_at": m.started_at,
                    "completed_at": m.completed_at,
                    "provider": m.provider_name,
                    "model": m.model,
                    "input_tokens": m.input_tokens,
                    "output_tokens": m.output_tokens,
                    "error": m.error,
                }
                for name, m in self.metadata.items()
            },
        }
