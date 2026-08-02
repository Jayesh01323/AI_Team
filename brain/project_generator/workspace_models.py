import datetime

from pydantic import BaseModel, Field


class WorkspaceFile(BaseModel):
    relative_path: str
    checksum: str
    template_id: str = ""
    size: int = 0

class WorkspaceDirectory(BaseModel):
    path: str
    directories: list['WorkspaceDirectory'] = Field(default_factory=list)
    files: list[WorkspaceFile] = Field(default_factory=list)

class Workspace(BaseModel):
    root_path: str
    directories: list[WorkspaceDirectory] = Field(default_factory=list)
    files: list[WorkspaceFile] = Field(default_factory=list)

class WorkspaceManifest(BaseModel):
    project_name: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())
    files: list[WorkspaceFile] = Field(default_factory=list)
    total_files: int = 0
    total_directories: int = 0
    checksums: dict[str, str] = Field(default_factory=dict)

class ExportStatistics(BaseModel):
    files_written: int = 0
    directories_written: int = 0
    bytes_written: int = 0
    skipped_files: int = 0
    overwritten_files: int = 0

class ExportResult(BaseModel):
    success: bool
    errors: list[str] = Field(default_factory=list)
    manifest: WorkspaceManifest | None = None
    statistics: ExportStatistics = Field(default_factory=ExportStatistics)
    destination: str

WorkspaceDirectory.model_rebuild()
