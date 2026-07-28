"""
Canonical ProjectSpecification domain model.

Aggregates Idea, Requirements, and PRD into a single validated document.
"""

from dataclasses import dataclass

from models.idea import Idea
from models.prd import PRD
from models.requirements import Requirements


@dataclass(frozen=True)
class ProjectSpecification:
    """
    ProjectSpecification aggregates all preceding stage outputs.

    Provides a unified model representing the complete, validated project specification.
    """

    idea: Idea
    requirements: Requirements
    prd: PRD

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "project_title": self.idea.title,
            "idea": self.idea.to_dict(),
            "requirements": self.requirements.to_dict(),
            "prd": self.prd.to_dict(),
        }
