import copy

from brain.project_generator.models import ProjectBlueprint

from .assembly_models import (
    AssembledProject,
    AssemblyStatistics,
    AssemblySummary,
    ProjectDirectory,
    ProjectFile,
)
from .code_models import GeneratedProject


class ProjectAssembler:
    def assemble(self, blueprint: ProjectBlueprint, generated_project: GeneratedProject) -> AssembledProject:
        root = ProjectDirectory(name=blueprint.project_name)
        dir_map: dict[str, ProjectDirectory] = {"": root}
        
        total_files = 0
        total_dirs = 0
        
        sorted_files = sorted(generated_project.generated_files, key=lambda f: f.path)
        
        for gf in sorted_files:
            path_parts = gf.path.strip("/").split("/")
            filename = path_parts[-1]
            dir_parts = path_parts[:-1]
            
            current_path = ""
            current_dir = root
            
            for part in dir_parts:
                next_path = f"{current_path}/{part}" if current_path else part
                if next_path not in dir_map:
                    new_dir = ProjectDirectory(name=part)
                    current_dir.directories.append(new_dir)
                    dir_map[next_path] = new_dir
                    total_dirs += 1
                current_dir = dir_map[next_path]
                current_path = next_path
                
            pf = ProjectFile(
                name=filename,
                content=gf.content,
                metadata=copy.deepcopy(gf.metadata),
                checksum=gf.checksum,
                template_id=gf.template_id
            )
            current_dir.files.append(pf)
            total_files += 1
            
        def sort_dir(d: ProjectDirectory):
            d.directories.sort(key=lambda x: x.name)
            d.files.sort(key=lambda x: x.name)
            for sub_d in d.directories:
                sort_dir(sub_d)
                
        sort_dir(root)
        
        stats = AssemblyStatistics(total_files=total_files, total_directories=total_dirs)
        summary = AssemblySummary(statistics=stats, description="Deterministic assembly completed")
        
        return AssembledProject(
            project_name=blueprint.project_name,
            root=root,
            summary=summary
        )
