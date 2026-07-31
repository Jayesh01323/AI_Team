from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

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
    dependencies: List[str] = Field(default_factory=list)
    subtasks: List[Subtask] = Field(default_factory=list)
    estimated_complexity: int = 1
    priority_score: float = 0.0
    execution_order: int = -1
    blockers: List[str] = Field(default_factory=list)

class Feature(BaseModel):
    id: str
    title: str
    tasks: List[Task] = Field(default_factory=list)

class Epic(BaseModel):
    id: str
    title: str
    features: List[Feature] = Field(default_factory=list)

class Milestone(BaseModel):
    id: str
    title: str
    epics: List[Epic] = Field(default_factory=list)

class Plan(BaseModel):
    project_name: str = "Unknown"
    milestones: List[Milestone] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
