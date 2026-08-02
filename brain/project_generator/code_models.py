import hashlib
from typing import Any

from pydantic import BaseModel, Field


class CodeGenerationValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)

class GeneratedFile(BaseModel):
    path: str
    filename: str
    content: str
    language: str = ""
    category: str = ""
    component: str = ""
    template_id: str = ""
    generated_from: str = ""
    checksum: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def calculate_checksum(self) -> str:
        return hashlib.sha256(self.content.encode('utf-8')).hexdigest()

class GeneratedProject(BaseModel):
    generated_files: list[GeneratedFile] = Field(default_factory=list)
    generation_summary: str = ""
    generation_metadata: dict[str, Any] = Field(default_factory=dict)
    validation_result: CodeGenerationValidationResult | None = None

    def export_dict(self) -> dict[str, Any]:
        return self.model_dump()
        
    def export_json(self) -> str:
        return self.model_dump_json(indent=2)
        
    def summary(self) -> str:
        valid = self.validation_result.is_valid if self.validation_result else False
        return f"Generated {len(self.generated_files)} files. Valid: {valid}"
