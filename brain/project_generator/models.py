
from pydantic import BaseModel, Field

from brain.architecture.models import Architecture
from brain.planner.models import Plan
from brain.specification.models import LivingSpecification


class GeneratedFile(BaseModel):
    path: str = Field(..., description="Relative path in the project")
    content: str = Field(..., description="File content")
    is_executable: bool = Field(default=False)

class ProjectBlueprint(BaseModel):
    project_name: str
    specification: LivingSpecification | None = Field(None, description="The Living Specification")
    plan: Plan | None = Field(None, description="The Plan")
    architecture: Architecture | None = Field(None, description="The Architecture")

class GeneratorContext(BaseModel):
    blueprint: ProjectBlueprint
    original_intent: str | None = Field(None, description="Read-only context")
    generated_files: list[GeneratedFile] = Field(default_factory=list)

class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
