from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentType(str, Enum):
    PLANNER = "planner"
    ARCHITECT = "architect"
    CODING = "coding"
    REVIEW = "review"
    TEST = "test"
    DOCUMENTATION = "documentation"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskAssignment(BaseModel):
    task_id: str
    agent_type: AgentType
    status: ExecutionStatus = ExecutionStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None

class Workflow(BaseModel):
    id: str
    assignments: Dict[str, TaskAssignment] = Field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    
class AgentRegistration(BaseModel):
    id: str
    agent_type: AgentType
    description: str
    capabilities: List[str] = Field(default_factory=list)

class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
