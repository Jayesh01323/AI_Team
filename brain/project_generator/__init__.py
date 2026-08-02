"""
Project Generator package.
Responsible for transforming the approved blueprint into a complete runnable project.
"""

from .assembler import ProjectAssembler
from .assembly_exporter import AssemblyExporter
from .assembly_models import (
    AssembledProject,
    AssemblyValidationResult,
    ProjectDirectory,
    ProjectFile,
)
from .assembly_validator import AssemblyValidator
from .code_generator import CodeGenerator
from .code_models import CodeGenerationValidationResult, GeneratedFile, GeneratedProject
from .code_renderer import CodeRenderer
from .code_validator import CodeValidator
from .export_validator import ExportValidator
from .pipeline import ProjectGenerationPipeline
from .pipeline_models import (
    PipelineExecution,
    PipelineResult,
    PipelineStage,
    PipelineStatistics,
)
from .pipeline_validator import PipelineValidator
from .project_exporter import ProjectExporter
from .repair_planner import RepairPlanner
from .template_matcher import TemplateMatcher
from .template_models import (
    ResolvedTemplateSet,
    TemplateMetadata,
    TemplateValidationResult,
)
from .template_registry import TemplateRegistry
from .template_resolver import TemplateResolver
from .validation_exporter import ValidationExporter
from .validation_models import (
    IssueCategory,
    RepairAction,
    RepairActionType,
    RepairPlan,
    RepairStatistics,
    Severity,
    ValidationIssue,
    ValidationReport,
    ValidationStatistics,
)
from .validator import EngineValidator
from .workspace_manager import WorkspaceManager
from .workspace_models import (
    ExportResult,
    ExportStatistics,
    Workspace,
    WorkspaceDirectory,
    WorkspaceFile,
    WorkspaceManifest,
)

__all__ = [
    "AssembledProject",
    "AssemblyExporter",
    "AssemblyValidationResult",
    "AssemblyValidator",
    "CodeGenerationValidationResult",
    "CodeGenerator",
    "CodeRenderer",
    "CodeValidator",
    "EngineValidator",
    "ExportResult",
    "ExportStatistics",
    "ExportValidator",
    "GeneratedFile",
    "GeneratedProject",
    "IssueCategory",
    "PipelineExecution",
    "PipelineResult",
    "PipelineStage",
    "PipelineStatistics",
    "PipelineValidator",
    "ProjectAssembler",
    "ProjectDirectory",
    "ProjectExporter",
    "ProjectFile",
    "ProjectGenerationPipeline",
    "RepairAction",
    "RepairActionType",
    "RepairPlan",
    "RepairPlanner",
    "RepairStatistics",
    "ResolvedTemplateSet",
    "Severity",
    "TemplateMatcher",
    "TemplateMetadata",
    "TemplateRegistry",
    "TemplateResolver",
    "TemplateValidationResult",
    "ValidationExporter",
    "ValidationIssue",
    "ValidationReport",
    "ValidationStatistics",
    "Workspace",
    "WorkspaceDirectory",
    "WorkspaceFile",
    "WorkspaceManager",
    "WorkspaceManifest"
]

