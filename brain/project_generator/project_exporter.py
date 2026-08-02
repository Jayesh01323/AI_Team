import os

from .assembly_models import AssembledProject
from .export_validator import ExportValidator
from .workspace_manager import WorkspaceManager
from .workspace_models import ExportResult, ExportStatistics, WorkspaceManifest


class ProjectExporter:
    def __init__(self, overwrite: bool = False):
        self.overwrite = overwrite
        self.validator = ExportValidator()
        self.manager = WorkspaceManager(overwrite=overwrite)

    def export(self, project: AssembledProject, destination: str) -> ExportResult:
        is_safe, errors = self.validator.validate_export_safety(project, destination)
        if not is_safe:
            return ExportResult(success=False, errors=errors, destination=destination)

        ws = self.manager.build_workspace_model(project, destination)
        manifest = self.manager.create_manifest(project, ws)
        
        stats = ExportStatistics()
        
        try:
            # Create directories first
            os.makedirs(ws.root_path, exist_ok=True)
            stats.directories_written += 1
            
            def create_dirs(dirs):
                for d in dirs:
                    os.makedirs(d.path, exist_ok=True)
                    stats.directories_written += 1
                    create_dirs(d.directories)
            create_dirs(ws.directories)

            # We need to map relative paths to actual project files to write their content
            file_contents = {}
            def extract_contents(p_dir, rel_base=""):
                for f in p_dir.files:
                    path = f"{rel_base}/{f.name}" if rel_base else f.name
                    file_contents[path] = f.content
                for sub in p_dir.directories:
                    sub_rel = f"{rel_base}/{sub.name}" if rel_base else sub.name
                    extract_contents(sub, sub_rel)
            extract_contents(project.root)

            # Write files
            for wf in ws.files:
                full_path = os.path.normpath(os.path.join(ws.root_path, wf.relative_path))
                
                if os.path.exists(full_path):
                    if not self.overwrite:
                        stats.skipped_files += 1
                        continue
                    stats.overwritten_files += 1
                
                content = file_contents.get(wf.relative_path, "")
                with open(full_path, "w", encoding="utf-8") as file:
                    file.write(content)
                    
                stats.files_written += 1
                stats.bytes_written += wf.size

        except Exception as e:
            return ExportResult(success=False, errors=[str(e)], manifest=manifest, statistics=stats, destination=destination)

        return ExportResult(success=True, manifest=manifest, statistics=stats, destination=destination)

    def export_to_directory(self, project: AssembledProject, destination: str) -> ExportResult:
        return self.export(project, destination)

    def export_manifest(self, project: AssembledProject, destination: str) -> WorkspaceManifest:
        ws = self.manager.build_workspace_model(project, destination)
        return self.manager.create_manifest(project, ws)
