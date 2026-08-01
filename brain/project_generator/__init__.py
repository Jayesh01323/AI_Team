"""
Project Generator package.
Responsible for transforming the approved blueprint into a complete runnable project.
"""

from .template_models import TemplateMetadata, ResolvedTemplateSet, TemplateValidationResult
from .template_registry import TemplateRegistry
from .template_matcher import TemplateMatcher
from .template_resolver import TemplateResolver

from .template_models import TemplateMetadata, ResolvedTemplateSet, TemplateValidationResult
from .template_registry import TemplateRegistry
from .template_matcher import TemplateMatcher
from .template_resolver import TemplateResolver

from .code_models import GeneratedFile, GeneratedProject, CodeGenerationValidationResult
from .code_generator import CodeGenerator
from .code_renderer import CodeRenderer
from .code_validator import CodeValidator

from .assembly_models import AssembledProject, ProjectDirectory, ProjectFile, AssemblyValidationResult
from .assembler import ProjectAssembler
from .assembly_validator import AssemblyValidator
from .assembly_exporter import AssemblyExporter

__all__ = [
    "TemplateMetadata",
    "ResolvedTemplateSet", 
    "TemplateValidationResult",
    "TemplateRegistry",
    "TemplateMatcher",
    "TemplateResolver",
    "GeneratedFile",
    "GeneratedProject",
    "CodeGenerationValidationResult",
    "CodeGenerator",
    "CodeRenderer",
    "CodeValidator",
    "AssembledProject",
    "ProjectDirectory",
    "ProjectFile",
    "AssemblyValidationResult",
    "ProjectAssembler",
    "AssemblyValidator",
    "AssemblyExporter"
]
