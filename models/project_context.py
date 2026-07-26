"""
ProjectContext — progressively accumulates all Engineering Brain stage outputs.

Each stage (Idea Analysis, Requirements, PRD, Architecture, etc.) reads the
current context and writes its output back. The context grows as stages complete.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from models.idea import Idea


@dataclass
class StageMetadata:
    """Metadata about a single stage execution."""

    stage_name: str
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    provider_name: Optional[str] = None
    model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    error: Optional[str] = None


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
    idea: Optional[Idea] = None
    # Future stages will add: requirements, prd, architecture, tech_stack, task_plan

    # Stage execution metadata
    metadata: dict[str, StageMetadata] = field(default_factory=dict)

    # Project identification
    project_name: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"
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

    def start_stage(self, name: str, provider_name: Optional[str] = None, model: Optional[str] = None) -> None:
        """Mark a stage as running."""
        stage = self.get_stage(name)
        stage.status = "running"
        stage.started_at = datetime.utcnow().isoformat() + "Z"
        if provider_name:
            stage.provider_name = provider_name
        if model:
            stage.model = model

    def complete_stage(
        self,
        name: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
    ) -> None:
        """Mark a stage as completed."""
        stage = self.get_stage(name)
        stage.status = "completed"
        stage.completed_at = datetime.utcnow().isoformat() + "Z"
        if input_tokens is not None:
            stage.input_tokens = input_tokens
        if output_tokens is not None:
            stage.output_tokens = output_tokens

    def fail_stage(self, name: str, error: str) -> None:
        """Mark a stage as failed."""
        stage = self.get_stage(name)
        stage.status = "failed"
        stage.completed_at = datetime.utcnow().isoformat() + "Z"
        stage.error = error

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "project_name": self.project_name,
            "raw_idea": self.raw_idea,
            "created_at": self.created_at,
            "idea": self.idea.to_dict() if self.idea else None,
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