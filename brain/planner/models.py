from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    READY = "ready"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Subtask(BaseModel):
    id: str
    title: str
    is_completed: bool = False

class Task(BaseModel):
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    dependencies: list[str] = Field(default_factory=list)
    subtasks: list[Subtask] = Field(default_factory=list)
    estimated_complexity: int = 1
    priority_score: float = 0.0
    execution_order: int = -1
    blockers: list[str] = Field(default_factory=list)

class Feature(BaseModel):
    id: str
    title: str
    tasks: list[Task] = Field(default_factory=list)

class Epic(BaseModel):
    id: str
    title: str
    features: list[Feature] = Field(default_factory=list)

class Milestone(BaseModel):
    id: str
    title: str
    epics: list[Epic] = Field(default_factory=list)

class Plan(BaseModel):
    project_name: str = "Unknown"
    milestones: list[Milestone] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
