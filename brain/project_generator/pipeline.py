"""
Project Generation Pipeline — Deterministic Code Generation.

Transforms a ProjectBlueprint into a complete, validated, exported project.
This pipeline operates on pre-defined templates and does NOT use LLM inference.

ARCHITECTURE BOUNDARY:
-----------------------
This is the DETERMINISTIC GENERATION path, distinct from:

  - pipeline/engine.py (PipelineEngine): LLM-powered analysis pipeline
      Purpose: Transform raw ideas into structured models using AI
      Stages: Idea Analysis → Requirements → PRD → Architecture → Task Planning
      Input: Raw idea text
      Output: ProjectContext with structured domain models

  - brain/project_generator/pipeline.py (ProjectGenerationPipeline): Deterministic generation
      Purpose: Generate actual code from approved blueprints
      Stages: Template Resolution → Code Generation → Assembly → Validation → Repair → Export
      Input: ProjectBlueprint (from Engineering Brain output)
      Output: Generated project files on disk

DO NOT mix these two pipelines. They serve different phases of the workflow.
"""

from typing import Optional

from .assembler import ProjectAssembler
from .code_generator import CodeGenerator
from .models import ProjectBlueprint
from .pipeline_models import PipelineExecution, PipelineResult, PipelineStage
from .pipeline_validator import PipelineValidator
from .project_exporter import ProjectExporter
from .repair_planner import RepairPlanner
from .template_registry import TemplateRegistry
from .template_resolver import TemplateResolver
from .validator import EngineValidator


class ProjectGenerationPipeline:
    """
    Deterministic project generation from blueprints.
    
    This pipeline generates code from templates without LLM inference.
    For AI-powered idea analysis, use pipeline.engine.PipelineEngine instead.
    """

    def __init__(self, overwrite_export: bool = False):
        self.registry = TemplateRegistry()
        self.resolver = TemplateResolver(self.registry)
        self.generator = CodeGenerator()
        self.assembler = ProjectAssembler()
        self.validator = EngineValidator()
        self.planner = RepairPlanner()
        self.exporter = ProjectExporter(overwrite=overwrite_export)
        self.pipe_validator = PipelineValidator()

    def run(self, blueprint: ProjectBlueprint, destination: str) -> PipelineResult:
        """
        Execute the deterministic project generation pipeline.
        
        Args:
            blueprint: ProjectBlueprint defining the project structure
            destination: Directory path where the project will be generated
            
        Returns:
            PipelineResult with generation statistics and any errors
        """
        return self._run_pipeline(blueprint, destination)
    
    def generate(self, blueprint: ProjectBlueprint, destination: str) -> PipelineResult:
        """
        DEPRECATED: Use run() instead.
        
        This method is kept for backwards compatibility but will be removed in v0.2.0.
        """
        import warnings
        warnings.warn(
            "ProjectGenerationPipeline.generate() is deprecated. Use run() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.run(blueprint, destination)
    
    def execute(self, blueprint: ProjectBlueprint, destination: str) -> PipelineResult:
        """
        DEPRECATED: Use run() instead.
        
        This method is kept for backwards compatibility but will be removed in v0.2.0.
        """
        import warnings
        warnings.warn(
            "ProjectGenerationPipeline.execute() is deprecated. Use run() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.run(blueprint, destination)

    def _run_pipeline(self, blueprint: ProjectBlueprint, destination: str) -> PipelineResult:
        result = PipelineResult(blueprint=blueprint)
        execution = PipelineExecution()
        
        # 1. Template Resolution
        if not self._execute_stage(execution, "Template Resolution", 1, result):
            return result
            
        try:
            resolved_templates = self.resolver.resolve_templates(blueprint)
            result.resolved_templates = resolved_templates
            self._complete_stage(execution, True, f"Resolved {len(resolved_templates.selected_templates)} templates")
        except Exception as e:
            self._complete_stage(execution, False, "Failed to resolve templates", [str(e)])
            result.errors.append(str(e))
            return self._finalize_result(result, execution)
            
        # 2. Code Generation
        if not self._execute_stage(execution, "Code Generation", 2, result):
            return result
            
        is_dep_valid, dep_errors = self.pipe_validator.validate_dependency(result.resolved_templates, "resolved_templates")
        if not is_dep_valid:
            self._complete_stage(execution, False, "Dependency validation failed", dep_errors)
            return self._finalize_result(result, execution)
            
        try:
            generated = self.generator.generate(blueprint, result.resolved_templates)
            result.generated_project = generated
            result.statistics.generated_files = len(generated.generated_files)
            self._complete_stage(execution, True, f"Generated {len(generated.generated_files)} files")
        except Exception as e:
            self._complete_stage(execution, False, "Failed to generate code", [str(e)])
            result.errors.append(str(e))
            return self._finalize_result(result, execution)
            
        # 3. Project Assembly
        if not self._execute_stage(execution, "Project Assembly", 3, result):
            return result
            
        is_dep_valid, dep_errors = self.pipe_validator.validate_dependency(result.generated_project, "generated_project")
        if not is_dep_valid:
            self._complete_stage(execution, False, "Dependency validation failed", dep_errors)
            return self._finalize_result(result, execution)
            
        try:
            assembled = self.assembler.assemble(blueprint, result.generated_project)
            result.assembled_project = assembled
            self._complete_stage(execution, True, "Assembled project structure")
        except Exception as e:
            self._complete_stage(execution, False, "Failed to assemble project", [str(e)])
            result.errors.append(str(e))
            return self._finalize_result(result, execution)
            
        # 4. Validation
        if not self._execute_stage(execution, "Validation", 4, result):
            return result
            
        is_dep_valid, dep_errors = self.pipe_validator.validate_dependency(result.assembled_project, "assembled_project")
        if not is_dep_valid:
            self._complete_stage(execution, False, "Dependency validation failed", dep_errors)
            return self._finalize_result(result, execution)
            
        try:
            val_report = self.validator.validate(blueprint, result.assembled_project)
            result.validation_report = val_report
            result.statistics.validation_issues = len(val_report.issues)
            self._complete_stage(execution, True, f"Validated with {len(val_report.issues)} issues")
        except Exception as e:
            self._complete_stage(execution, False, "Validation failed", [str(e)])
            result.errors.append(str(e))
            return self._finalize_result(result, execution)
            
        # 5. Repair Planning
        if not self._execute_stage(execution, "Repair Planning", 5, result):
            return result
            
        is_dep_valid, dep_errors = self.pipe_validator.validate_dependency(result.validation_report, "validation_report")
        if not is_dep_valid:
            self._complete_stage(execution, False, "Dependency validation failed", dep_errors)
            return self._finalize_result(result, execution)
            
        try:
            plan = self.planner.plan_repairs(result.validation_report)
            result.repair_plan = plan
            result.statistics.repair_actions = len(plan.actions)
            self._complete_stage(execution, True, f"Planned {len(plan.actions)} repairs")
        except Exception as e:
            self._complete_stage(execution, False, "Repair planning failed", [str(e)])
            result.errors.append(str(e))
            return self._finalize_result(result, execution)

        # 6. Export Project (Only if valid, based on constraints: "Only export validated projects")
        if not self._execute_stage(execution, "Project Export", 6, result):
            return result
            
        if not result.validation_report.is_valid:
            self._complete_stage(execution, False, "Skipped export due to validation failures", ["Project is invalid"])
            # Returning here means the pipeline finishes with success=False, but captures everything up to Repair Planning
            return self._finalize_result(result, execution)
            
        try:
            export_result = self.exporter.export(result.assembled_project, destination)
            result.export_result = export_result
            if export_result.success:
                result.workspace_manifest = export_result.manifest
                result.statistics.exported_files = export_result.statistics.files_written
                self._complete_stage(execution, True, f"Exported {export_result.statistics.files_written} files")
            else:
                self._complete_stage(execution, False, "Export failed", export_result.errors)
                result.errors.extend(export_result.errors)
        except Exception as e:
            self._complete_stage(execution, False, "Export stage error", [str(e)])
            result.errors.append(str(e))
            
        result.success = bool(len(result.errors) == 0 and result.export_result and result.export_result.success)
        return self._finalize_result(result, execution)

    def _execute_stage(self, execution: PipelineExecution, name: str, order: int, result: PipelineResult) -> bool:
        is_valid, errors = self.pipe_validator.validate_stage_transition(execution, name, order)
        if not is_valid:
            result.errors.extend(errors)
            return False
            
        # Push stage as running/in-progress
        stage = PipelineStage(name=name, execution_order=order)
        execution.stages.append(stage)
        return True
        
    def _complete_stage(self, execution: PipelineExecution, success: bool, summary: str, errors: Optional[list] = None):
        if len(execution.stages) > 0:
            stage = execution.stages[-1]
            stage.success = success
            stage.summary = summary
            if errors:
                stage.errors.extend(errors)

    def _finalize_result(self, result: PipelineResult, execution: PipelineExecution) -> PipelineResult:
        result.stage_summaries = execution.stages
        
        # Calculate statistics
        result.statistics.total_stages = len(execution.stages)
        result.statistics.successful_stages = sum(1 for s in execution.stages if s.success)
        result.statistics.failed_stages = sum(1 for s in execution.stages if not s.success)
        result.statistics.total_execution_order = sum(s.execution_order for s in execution.stages)
        
        # If any stage failed, result is not successful
        if result.statistics.failed_stages > 0:
            result.success = False
            
        return result
