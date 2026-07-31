from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
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
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Decision(BaseModel):
    id: str
    title: str
    description: str
    status: EntityStatus = EntityStatus.PROPOSED
    rationale: Optional[str] = None
    alternatives_considered: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

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
    goals: List[str] = Field(default_factory=list)
    
    # 6. Success Criteria
    success_criteria: List[str] = Field(default_factory=list)
    
    # 7. Target Users
    target_users: List[str] = Field(default_factory=list)
    
    # 8. Personas
    personas: List[Persona] = Field(default_factory=list)
    
    # 9. Functional Requirements
    functional_requirements: List[Requirement] = Field(default_factory=list)
    
    # 10. Non-functional Requirements
    non_functional_requirements: List[Requirement] = Field(default_factory=list)
    
    # 11. Constraints
    constraints: List[Constraint] = Field(default_factory=list)
    
    # 12. Assumptions
    assumptions: List[str] = Field(default_factory=list)
    
    # 13. Open Questions
    open_questions: List[str] = Field(default_factory=list)
    
    # 14-16. Decisions
    accepted_decisions: List[Decision] = Field(default_factory=list)
    rejected_decisions: List[Decision] = Field(default_factory=list)
    superseded_decisions: List[Decision] = Field(default_factory=list)
    
    # 17. Technology Stack
    technology_stack: Dict[str, str] = Field(default_factory=dict)
    
    # 18. Architecture Summary
    architecture_summary: str = ""
    
    # 19. Risks
    risks: List[str] = Field(default_factory=list)
    
    # 20. Dependencies
    dependencies: List[str] = Field(default_factory=list)
    
    # 21. Milestones
    milestones: List[str] = Field(default_factory=list)
    
    # 22. Current Project State
    current_state: str = "Initializing"
    
    # 23. Confidence Summary
    confidence_score: float = 0.0
    
    # 24. Last Updated Timestamp
    last_updated: datetime = Field(default_factory=datetime.utcnow)

