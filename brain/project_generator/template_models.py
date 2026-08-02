from typing import Any

from pydantic import BaseModel, Field


class TemplateValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)

class TemplateMetadata(BaseModel):
    id: str
    name: str
    category: str
    supported_project_types: list[str] = Field(default_factory=list)
    supported_languages: list[str] = Field(default_factory=list)
    supported_frameworks: list[str] = Field(default_factory=list)
    supported_databases: list[str] = Field(default_factory=list)
    supported_frontends: list[str] = Field(default_factory=list)
    supported_backends: list[str] = Field(default_factory=list)
    supported_deployment: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    priority: int = 0
    version: str = "1.0.0"

class ResolvedTemplateSet(BaseModel):
    selected_templates: list[TemplateMetadata] = Field(default_factory=list)
    selection_rationale: dict[str, str] = Field(default_factory=dict)
    dependency_ordering: list[str] = Field(default_factory=list)
    validation_result: TemplateValidationResult | None = Field(default=None)

    def export_dict(self) -> dict[str, Any]:
        return self.model_dump()
        
    def export_json(self) -> str:
        return self.model_dump_json(indent=2)
        
    def summary(self) -> str:
        ids = [t.id for t in self.selected_templates]
        valid = self.validation_result.is_valid if self.validation_result else False
        return f"Resolved {len(ids)} templates: {', '.join(ids)}. Valid: {valid}"
