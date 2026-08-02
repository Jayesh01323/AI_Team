import os

from .assembly_models import AssembledProject, ProjectDirectory
from .workspace_models import (
    Workspace,
    WorkspaceDirectory,
    WorkspaceFile,
    WorkspaceManifest,
)


class WorkspaceManager:
    def __init__(self, overwrite: bool = False):
        self.overwrite = overwrite

    def build_workspace_model(self, project: AssembledProject, destination: str) -> Workspace:
        dest_norm = os.path.normpath(os.path.abspath(destination))
        
        ws = Workspace(root_path=dest_norm)
        
        # Add root files
        for f in sorted(project.root.files, key=lambda x: x.name):
            ws_f = WorkspaceFile(
                relative_path=f.name,
                checksum=f.checksum,
                template_id=f.template_id,
                size=len(f.content.encode('utf-8'))
            )
            ws.files.append(ws_f)
            
        ws.directories = self._convert_directory(project.root, dest_norm)
        
        # Flatten for easy manifest creation
        all_files = ws.files + self._collect_workspace_files(ws.directories)
        
        # Deterministic sorting
        all_files.sort(key=lambda x: x.relative_path)
        ws.files = all_files
        
        return ws
        
    def create_manifest(self, project: AssembledProject, ws: Workspace) -> WorkspaceManifest:
        checksums = {}
        for f in ws.files:
            checksums[f.relative_path] = f.checksum
            
        return WorkspaceManifest(
            project_name=project.project_name,
            files=ws.files,
            total_files=len(ws.files),
            total_directories=self._count_directories(ws.directories),
            checksums=checksums
        )

    def _convert_directory(self, project_dir: ProjectDirectory, current_path: str, rel_base: str = "") -> list[WorkspaceDirectory]:
        result = []
        for subdir in sorted(project_dir.directories, key=lambda d: d.name):
            sub_path = os.path.join(current_path, subdir.name)
            sub_rel = f"{rel_base}/{subdir.name}" if rel_base else subdir.name
            
            ws_dir = WorkspaceDirectory(path=sub_path)
            
            # files in this subdir
            for f in sorted(subdir.files, key=lambda x: x.name):
                f_rel = f"{sub_rel}/{f.name}"
                ws_f = WorkspaceFile(
                    relative_path=f_rel,
                    checksum=f.checksum,
                    template_id=f.template_id,
                    size=len(f.content.encode('utf-8'))
                )
                ws_dir.files.append(ws_f)
                
            ws_dir.directories = self._convert_directory(subdir, sub_path, sub_rel)
            result.append(ws_dir)
            
        return result

    def _collect_workspace_files(self, dirs: list[WorkspaceDirectory]) -> list[WorkspaceFile]:
        files = []
        for d in dirs:
            files.extend(d.files)
            files.extend(self._collect_workspace_files(d.directories))
        return files

    def _count_directories(self, dirs: list[WorkspaceDirectory]) -> int:
        count = len(dirs)
        for d in dirs:
            count += self._count_directories(d.directories)
        return count
