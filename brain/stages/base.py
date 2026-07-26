"""
Abstract base class for all Engineering Brain stages.

A Stage is a single pipeline step that reads from ProjectContext
and writes its output back to it.

Architecture:

    Stage 1: Idea Analyzer
        ProjectContext(raw_idea) -> ProjectContext(idea=Idea(...))

    Stage 2: Requirements Generator
        ProjectContext(idea=Idea(...)) -> ProjectContext(idea=..., requirements=...)

    Stage 3: PRD Generator
        ProjectContext(...) -> ProjectContext(..., prd=...)

    etc.
"""

from abc import ABC, abstractmethod

from models.project_context import ProjectContext


class Stage(ABC):
    """Abstract interface for an Engineering Brain pipeline stage."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stage name (e.g. 'idea_analysis')."""
        ...

    @abstractmethod
    def execute(self, context: ProjectContext) -> ProjectContext:
        """
        Execute this stage, reading from and writing to the context.

        Args:
            context: The current ProjectContext with accumulated outputs.

        Returns:
            The updated ProjectContext with this stage's output added.

        Raises:
            ProviderError: If the provider fails.
            ConfigurationError: If configuration is invalid.
        """
        ...

    def should_execute(self, context: ProjectContext) -> bool:
        """
        Check if this stage should run.

        Override to skip stages that have already completed.
        Default: always execute.
        """
        return True