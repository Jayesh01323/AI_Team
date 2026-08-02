from typing import Any

from pydantic import BaseModel, Field

from .assembly_models import AssembledProject
from .code_models import GeneratedProject
from .models import ProjectBlueprint
from .template_models import ResolvedTemplateSet
from .validation_models import RepairPlan, ValidationReport
from .workspace_models import ExportResult, WorkspaceManifest


class PipelineStage(BaseModel):
    name: str
    success: bool = False
    execution_order: int
    summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)

class PipelineExecution(BaseModel):
    stages: list[PipelineStage] = Field(default_factory=list)

class PipelineStatistics(BaseModel):
    total_stages: int = 0
    successful_stages: int = 0
    failed_stages: int = 0
    generated_files: int = 0
    exported_files: int = 0
    validation_issues: int = 0
    repair_actions: int = 0
    total_execution_order: int = 0

class PipelineResult(BaseModel):
    success: bool = False
    blueprint: ProjectBlueprint
    resolved_templates: ResolvedTemplateSet | None = None
    generated_project: GeneratedProject | None = None
    assembled_project: AssembledProject | None = None
    validation_report: ValidationReport | None = None
    repair_plan: RepairPlan | None = None
    export_result: ExportResult | None = None
    workspace_manifest: WorkspaceManifest | None = None
    statistics: PipelineStatistics = Field(default_factory=PipelineStatistics)
    stage_summaries: list[PipelineStage] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
