from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EntityStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    PROPOSED = "proposed"

class Requirement(BaseModel):
    id: str
    description: str
    priority: str = "medium"
    type: str = "functional"  # functional, non-functional
    metadata: dict[str, Any] = Field(default_factory=dict)

class Decision(BaseModel):
    id: str
    title: str
    description: str
    status: EntityStatus = EntityStatus.PROPOSED
    rationale: str | None = None
    alternatives_considered: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

class Constraint(BaseModel):
    id: str
    description: str
    type: str  # technical, business, time, etc.

class Persona(BaseModel):
    name: str
    role: str
    description: str

class LivingSpecification(BaseModel):
    """The central Living Specification Model."""
    
    # 1. Project Metadata
    project_name: str = "Unknown Project"
    version: str = "0.1.0"
    
    # 2. Vision
    vision: str = ""
    
    # 3. Mission
    mission: str = ""
    
    # 4. Problem Statement
    problem_statement: str = ""
    
    # 5. Goals
    goals: list[str] = Field(default_factory=list)
    
    # 6. Success Criteria
    success_criteria: list[str] = Field(default_factory=list)
    
    # 7. Target Users
    target_users: list[str] = Field(default_factory=list)
    
    # 8. Personas
    personas: list[Persona] = Field(default_factory=list)
    
    # 9. Functional Requirements
    functional_requirements: list[Requirement] = Field(default_factory=list)
    
    # 10. Non-functional Requirements
    non_functional_requirements: list[Requirement] = Field(default_factory=list)
    
    # 11. Constraints
    constraints: list[Constraint] = Field(default_factory=list)
    
    # 12. Assumptions
    assumptions: list[str] = Field(default_factory=list)
    
    # 13. Open Questions
    open_questions: list[str] = Field(default_factory=list)
    
    # 14-16. Decisions
    accepted_decisions: list[Decision] = Field(default_factory=list)
    rejected_decisions: list[Decision] = Field(default_factory=list)
    superseded_decisions: list[Decision] = Field(default_factory=list)
    
    # 17. Technology Stack
    technology_stack: dict[str, str] = Field(default_factory=dict)
    
    # 18. Architecture Summary
    architecture_summary: str = ""
    
    # 19. Risks
    risks: list[str] = Field(default_factory=list)
    
    # 20. Dependencies
    dependencies: list[str] = Field(default_factory=list)
    
    # 21. Milestones
    milestones: list[str] = Field(default_factory=list)
    
    # 22. Current Project State
    current_state: str = "Initializing"
    
    # 23. Confidence Summary
    confidence_score: float = 0.0
    
    # 24. Last Updated Timestamp
    last_updated: datetime = Field(default_factory=datetime.utcnow)

