from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class IssueCategory(str, Enum):
    Structure = "Structure"
    Metadata = "Metadata"
    Blueprint = "Blueprint"
    Assembly = "Assembly"
    Template = "Template"
    Architecture = "Architecture"
    GeneratedFile = "GeneratedFile"

class ValidationIssue(BaseModel):
    id: str
    type: str
    message: str
    severity: Severity
    target: str
    category: IssueCategory | None = None
    source_component: str | None = None
    suggested_action: str | None = None
    metadata: dict = Field(default_factory=dict)

class ValidationStatistics(BaseModel):
    total_issues: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    issues_by_category: dict[str, int] = Field(default_factory=dict)
    issues_by_severity: dict[str, int] = Field(default_factory=dict)

class ValidationReport(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    statistics: ValidationStatistics = Field(default_factory=ValidationStatistics)

class RepairActionType(str, Enum):
    CREATE_FILE = "CREATE_FILE"
    DELETE_FILE = "DELETE_FILE"
    MOVE_FILE = "MOVE_FILE"
    RENAME_FILE = "RENAME_FILE"
    REGENERATE_FILE = "REGENERATE_FILE"
    UPDATE_METADATA = "UPDATE_METADATA"
    REMOVE_DUPLICATE = "REMOVE_DUPLICATE"
    FIX_PLACEHOLDER = "FIX_PLACEHOLDER"

class RepairAction(BaseModel):
    id: str
    type: RepairActionType
    reason: str
    severity: Severity
    target: str
    deterministic_priority: int
    dependencies: list[str] = Field(default_factory=list)
    issue_id: str | None = None
    metadata: dict = Field(default_factory=dict)

class RepairStatistics(BaseModel):
    total_actions: int = 0
    actions_by_type: dict[str, int] = Field(default_factory=dict)
    actions_by_severity: dict[str, int] = Field(default_factory=dict)

class RepairPlan(BaseModel):
    actions: list[RepairAction] = Field(default_factory=list)
    statistics: RepairStatistics = Field(default_factory=RepairStatistics)

