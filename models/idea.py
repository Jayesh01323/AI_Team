"""
Canonical Idea domain model.

Represents a fully analyzed project idea with all its attributes.
The Idea Analyzer produces this model from raw user input.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Idea:
    """
    A fully analyzed project idea.

    All fields are populated by the Idea Analyzer after processing
    the user's raw idea input through an AI provider.
    """

    title: str
    """Short, descriptive title for the project."""

    summary: str
    """One-paragraph summary of what the project does."""

    target_users: list[str] = field(default_factory=list)
    """Who this project is for (e.g. ['solo founders', 'freelancers'])."""

    functional_requirements: list[str] = field(default_factory=list)
    """What the system must do — features and capabilities."""

    non_functional_requirements: list[str] = field(default_factory=list)
    """Quality attributes — performance, security, scalability, etc."""

    assumptions: list[str] = field(default_factory=list)
    """Things we assume to be true about the project context."""

    constraints: list[str] = field(default_factory=list)
    """Boundaries the project must operate within (budget, time, tech)."""

    risks: list[str] = field(default_factory=list)
    """Potential problems that could derail the project."""

    unknowns: list[str] = field(default_factory=list)
    """Things that need further investigation before proceeding."""

    clarification_questions: list[str] = field(default_factory=list)
    """Questions to ask the founder to fill gaps in the idea."""

    raw_idea: str = ""
    """The original raw idea text from the user."""

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "title": self.title,
            "summary": self.summary,
            "target_users": list(self.target_users),
            "functional_requirements": list(self.functional_requirements),
            "non_functional_requirements": list(self.non_functional_requirements),
            "assumptions": list(self.assumptions),
            "constraints": list(self.constraints),
            "risks": list(self.risks),
            "unknowns": list(self.unknowns),
            "clarification_questions": list(self.clarification_questions),
            "raw_idea": self.raw_idea,
        }
