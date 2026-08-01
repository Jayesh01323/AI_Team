from typing import Set, List
from .assembly_models import AssembledProject, AssemblyValidationResult, ProjectDirectory

class AssemblyValidator:
    def validate(self, project: AssembledProject) -> AssemblyValidationResult:
        errors = []
        
        seen_dirs: Set[str] = set()
        seen_files: Set[str] = set()
        
        def validate_dir(d: ProjectDirectory, current_path: str):
            dir_names = set()
            for sub_d in d.directories:
                if sub_d.name in dir_names:
                    errors.append(f"Duplicate directory name '{sub_d.name}' in {current_path}")
                dir_names.add(sub_d.name)
                
                full_path = f"{current_path}/{sub_d.name}" if current_path else sub_d.name
                if full_path in seen_dirs:
                    errors.append(f"Duplicate directory path detected: {full_path}")
                seen_dirs.add(full_path)
                
                validate_dir(sub_d, full_path)
                
            file_names = set()
            for f in d.files:
                if f.name in file_names:
                    errors.append(f"Duplicate file name '{f.name}' in {current_path}")
                file_names.add(f.name)
                
                full_path = f"{current_path}/{f.name}" if current_path else f.name
                if full_path in seen_files:
                    errors.append(f"Duplicate file path detected: {full_path}")
                seen_files.add(full_path)
                
        validate_dir(project.root, project.root.name)
        
        if not project.root.directories and not project.root.files:
            errors.append("Invalid project structure: root directory is empty")
            
        return AssemblyValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
