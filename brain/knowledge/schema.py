"""
Schema definition for a complete software project knowledge structure.

This module defines the expected high-level sections of a fully
populated ``ProjectKnowledge`` artifact. It is a declarative schema —
it describes WHAT sections should exist, not HOW they are populated.

Future Milestone 4 components can use this schema to:
- Validate completeness of a knowledge artifact
- Identify missing sections that need enrichment
- Provide a roadmap for progressive knowledge gathering
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SchemaSection:
    """
    A single section in the project knowledge schema.

    Attributes:
        name: Machine-readable section identifier.
        label: Human-readable label.
        description: What this section represents.
        required: Whether this section is required for a complete project.
        sub_sections: Nested sub-sections, if any.
    """

    name: str
    label: str
    description: str
    required: bool = False
    sub_sections: list[SchemaSection] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Sub-sections
# ---------------------------------------------------------------------------

_VISION_SECTION = SchemaSection(
    name="vision",
    label="Vision",
    description="The long-term vision and purpose of the project.",
    required=True,
)

_PROBLEM_SECTION = SchemaSection(
    name="problem",
    label="Problem Statement",
    description="The specific problem the project solves.",
    required=True,
)

_TARGET_USERS_SECTION = SchemaSection(
    name="target_users",
    label="Target Users",
    description="User segments and personas the project serves.",
    required=True,
)

_BUSINESS_GOALS_SECTION = SchemaSection(
    name="business_goals",
    label="Business Goals",
    description="Business objectives and success metrics.",
    required=True,
)

_FUNCTIONAL_REQUIREMENTS_SECTION = SchemaSection(
    name="functional_requirements",
    label="Functional Requirements",
    description="What the system must do — features and capabilities.",
    required=True,
)

_NON_FUNCTIONAL_REQUIREMENTS_SECTION = SchemaSection(
    name="non_functional_requirements",
    label="Non-Functional Requirements",
    description="Quality attributes — performance, security, scalability, etc.",
    required=True,
)

_ARCHITECTURE_SECTION = SchemaSection(
    name="architecture",
    label="Architecture",
    description="System architecture, components, and their relationships.",
    required=False,
)

_TECH_STACK_SECTION = SchemaSection(
    name="tech_stack",
    label="Technology Stack",
    description="Languages, frameworks, libraries, and tools chosen for the project.",
    required=False,
)

_DEPLOYMENT_SECTION = SchemaSection(
    name="deployment",
    label="Deployment",
    description="Deployment strategy, infrastructure, and environment details.",
    required=False,
)

_SECURITY_SECTION = SchemaSection(
    name="security",
    label="Security",
    description="Security requirements, threats, and mitigation strategies.",
    required=False,
)

_TESTING_SECTION = SchemaSection(
    name="testing",
    label="Testing",
    description="Testing strategy, coverage goals, and test types.",
    required=False,
)

_ROADMAP_SECTION = SchemaSection(
    name="roadmap",
    label="Roadmap",
    description="Project timeline, milestones, and delivery phases.",
    required=False,
)

_DECISIONS_SECTION = SchemaSection(
    name="decisions",
    label="Decisions",
    description="Architectural and product decisions with rationale.",
    required=False,
)

_CONSTRAINTS_SECTION = SchemaSection(
    name="constraints",
    label="Constraints",
    description="Budget, technical, time, and compliance constraints.",
    required=False,
)

_ASSUMPTIONS_SECTION = SchemaSection(
    name="assumptions",
    label="Assumptions",
    description="Assumptions made about the project context.",
    required=False,
)

_OPEN_QUESTIONS_SECTION = SchemaSection(
    name="open_questions",
    label="Open Questions",
    description="Unanswered questions that need resolution.",
    required=False,
)

_USER_PREFERENCES_SECTION = SchemaSection(
    name="user_preferences",
    label="User Preferences",
    description="User-specified preferences for languages, frameworks, etc.",
    required=False,
)


# ---------------------------------------------------------------------------
# Complete project schema
# ---------------------------------------------------------------------------

PROJECT_SCHEMA: list[SchemaSection] = [
    _VISION_SECTION,
    _PROBLEM_SECTION,
    _TARGET_USERS_SECTION,
    _BUSINESS_GOALS_SECTION,
    _FUNCTIONAL_REQUIREMENTS_SECTION,
    _NON_FUNCTIONAL_REQUIREMENTS_SECTION,
    _ARCHITECTURE_SECTION,
    _TECH_STACK_SECTION,
    _DEPLOYMENT_SECTION,
    _SECURITY_SECTION,
    _TESTING_SECTION,
    _ROADMAP_SECTION,
    _DECISIONS_SECTION,
    _CONSTRAINTS_SECTION,
    _ASSUMPTIONS_SECTION,
    _OPEN_QUESTIONS_SECTION,
    _USER_PREFERENCES_SECTION,
]


def get_required_sections() -> list[SchemaSection]:
    """Return only the sections marked as required."""
    return [s for s in PROJECT_SCHEMA if s.required]


def get_optional_sections() -> list[SchemaSection]:
    """Return only the sections marked as optional."""
    return [s for s in PROJECT_SCHEMA if not s.required]


def get_section_names() -> list[str]:
    """Return the machine-readable names of all schema sections."""
    return [s.name for s in PROJECT_SCHEMA]


def is_complete(knowledge: dict) -> dict[str, bool]:
    """
    Check which required sections are populated in a knowledge dictionary.

    Args:
        knowledge: A dictionary representation of a ProjectKnowledge model.

    Returns:
        A mapping of section name to boolean (True if populated).
    """
    result: dict[str, bool] = {}
    for section in PROJECT_SCHEMA:
        value = knowledge.get(section.name)
        if isinstance(value, str):
            result[section.name] = bool(value.strip())
        elif isinstance(value, list):
            result[section.name] = len(value) > 0
        elif isinstance(value, dict):
            result[section.name] = len(value) > 0
        else:
            result[section.name] = value is not None
    return result