from pydantic import BaseModel, Field
from typing import List, Optional
from brain.specification.models import LivingSpecification
from brain.planner.models import Plan
from brain.architecture.models import Architecture

class GeneratedFile(BaseModel):
    path: str = Field(..., description="Relative path in the project")
    content: str = Field(..., description="File content")
    is_executable: bool = Field(default=False)

class ProjectBlueprint(BaseModel):
    project_name: str
    specification: Optional[LivingSpecification] = Field(None, description="The Living Specification")
    plan: Optional[Plan] = Field(None, description="The Plan")
    architecture: Optional[Architecture] = Field(None, description="The Architecture")

class GeneratorContext(BaseModel):
    blueprint: ProjectBlueprint
    original_intent: Optional[str] = Field(None, description="Read-only context")
    generated_files: List[GeneratedFile] = Field(default_factory=list)

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
