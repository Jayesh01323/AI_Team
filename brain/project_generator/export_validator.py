import os

from .assembly_models import AssembledProject, ProjectDirectory, ProjectFile


class ExportValidator:
    def __init__(self):
        # Reserved filenames or extensions on windows/linux that might be problematic, but we mainly care about strict traversal
        pass

    def validate_export_safety(self, project: AssembledProject, destination: str) -> tuple[bool, list[str]]:
        errors = []
        
        if not destination or not destination.strip():
            errors.append("Destination path is empty")
            return False, errors
            
        dest_norm = os.path.normpath(os.path.abspath(destination))
        
        all_files = self._collect_all_files(project.root)
        
        seen_paths = set()
        
        for rel_path, file in all_files:
            if not rel_path or not rel_path.strip():
                errors.append(f"Empty relative path for file: {file.name}")
                continue
                
            if os.path.isabs(rel_path):
                errors.append(f"Absolute path not allowed: {rel_path}")
                continue
                
            # Traversal check
            norm_rel = os.path.normpath(rel_path)
            if norm_rel.startswith('..') or norm_rel == '..':
                errors.append(f"Path traversal detected: {rel_path}")
                continue
                
            # Windows reserved char check
            if any(c in file.name for c in ["<", ">", ":", "\"", "\\", "|", "?", "*"]):
                errors.append(f"Invalid characters in filename: {file.name}")
                
            if rel_path in seen_paths:
                errors.append(f"Duplicate path detected: {rel_path}")
            seen_paths.add(rel_path)
            
            # Combine to test resolution doesn't escape dest
            full_path = os.path.normpath(os.path.join(dest_norm, norm_rel))
            if os.path.commonpath([full_path, dest_norm]) != dest_norm:
                errors.append(f"Path resolves outside destination: {rel_path}")
                
        # Deterministic order
        errors.sort()
        return len(errors) == 0, errors

    def _collect_all_files(self, directory: ProjectDirectory, current_path: str = "") -> list[tuple[str, ProjectFile]]:
        files = []
        for file in directory.files:
            path = f"{current_path}/{file.name}" if current_path else file.name
            files.append((path, file))
        for subdir in directory.directories:
            path = f"{current_path}/{subdir.name}" if current_path else subdir.name
            files.extend(self._collect_all_files(subdir, path))
        return files
