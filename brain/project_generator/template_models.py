from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TemplateValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)

class TemplateMetadata(BaseModel):
    id: str
    name: str
    category: str
    supported_project_types: List[str] = Field(default_factory=list)
    supported_languages: List[str] = Field(default_factory=list)
    supported_frameworks: List[str] = Field(default_factory=list)
    supported_databases: List[str] = Field(default_factory=list)
    supported_frontends: List[str] = Field(default_factory=list)
    supported_backends: List[str] = Field(default_factory=list)
    supported_deployment: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    priority: int = 0
    version: str = "1.0.0"

class ResolvedTemplateSet(BaseModel):
    selected_templates: List[TemplateMetadata] = Field(default_factory=list)
    selection_rationale: Dict[str, str] = Field(default_factory=dict)
    dependency_ordering: List[str] = Field(default_factory=list)
    validation_result: Optional[TemplateValidationResult] = Field(default=None)

    def export_dict(self) -> Dict[str, Any]:
        return self.model_dump()
        
    def export_json(self) -> str:
        return self.model_dump_json(indent=2)
        
    def summary(self) -> str:
        ids = [t.id for t in self.selected_templates]
        valid = self.validation_result.is_valid if self.validation_result else False
        return f"Resolved {len(ids)} templates: {', '.join(ids)}. Valid: {valid}"
