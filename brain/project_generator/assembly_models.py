from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AssemblyValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)

class ProjectFile(BaseModel):
    name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    checksum: str = ""
    template_id: str = ""

class ProjectDirectory(BaseModel):
    name: str
    files: List[ProjectFile] = Field(default_factory=list)
    directories: List["ProjectDirectory"] = Field(default_factory=list)

class AssemblyStatistics(BaseModel):
    total_files: int = 0
    total_directories: int = 0
    
class AssemblySummary(BaseModel):
    statistics: AssemblyStatistics = Field(default_factory=AssemblyStatistics)
    description: str = ""

class AssembledProject(BaseModel):
    project_name: str
    root: ProjectDirectory
    summary: AssemblySummary = Field(default_factory=AssemblySummary)
    validation_result: Optional[AssemblyValidationResult] = None

    def export_dict(self) -> Dict[str, Any]:
        return self.model_dump()
        
    def export_json(self) -> str:
        return self.model_dump_json(indent=2)
        
    def summary_text(self) -> str:
        valid = self.validation_result.is_valid if self.validation_result else False
        stats = self.summary.statistics
        return f"AssembledProject: {self.project_name}, Dirs: {stats.total_directories}, Files: {stats.total_files}. Valid: {valid}"

ProjectDirectory.model_rebuild()
