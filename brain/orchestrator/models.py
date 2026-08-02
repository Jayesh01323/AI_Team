from enum import Enum
from typing import Any

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
    dependencies: list[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    error_message: str | None = None
    execution_result: dict[str, Any] | None = None

class Workflow(BaseModel):
    id: str
    assignments: dict[str, TaskAssignment] = Field(default_factory=dict)
    execution_history: list[dict[str, Any]] = Field(default_factory=list)
    
class AgentRegistration(BaseModel):
    id: str
    agent_type: AgentType
    description: str
    capabilities: list[str] = Field(default_factory=list)

class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
