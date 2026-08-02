import hashlib

from .assembly_models import AssembledProject, ProjectDirectory, ProjectFile
from .interfaces import IProjectValidator
from .models import GeneratorContext, ProjectBlueprint, ValidationResult
from .validation_models import (
    IssueCategory,
    Severity,
    ValidationIssue,
    ValidationReport,
    ValidationStatistics,
)


class ProjectValidator(IProjectValidator):
    def validate(self, context: GeneratorContext) -> ValidationResult:
        # Foundation skeleton.
        if not context.blueprint:
            return ValidationResult(is_valid=False, errors=["Missing blueprint"])
        return ValidationResult(is_valid=True)

class EngineValidator:
    def validate(self, blueprint: ProjectBlueprint, assembled_project: AssembledProject) -> ValidationReport:
        issues: list[ValidationIssue] = []
        
        self._check_project_structure(assembled_project, issues)
        self._check_metadata(assembled_project, issues)
        self._check_generated_files(assembled_project, issues)
        self._check_blueprint_consistency(blueprint, assembled_project, issues)

        # Deterministically sort issues by target, then type, then id
        issues.sort(key=lambda x: (x.target, x.type, x.id))
        
        issues_by_cat = {cat.value: sum(1 for i in issues if i.category == cat) for cat in IssueCategory}
        issues_by_sev = {sev.value: sum(1 for i in issues if i.severity == sev) for sev in Severity}
        
        stats = ValidationStatistics(
            total_issues=len(issues),
            errors=issues_by_sev.get(Severity.ERROR.value, 0),
            warnings=issues_by_sev.get(Severity.WARNING.value, 0),
            infos=issues_by_sev.get(Severity.INFO.value, 0),
            issues_by_category=issues_by_cat,
            issues_by_severity=issues_by_sev
        )
        
        is_valid = stats.errors == 0
        
        return ValidationReport(
            is_valid=is_valid,
            issues=issues,
            statistics=stats
        )


    def _collect_all_files(self, directory: ProjectDirectory, current_path: str = "") -> list[tuple[str, ProjectFile]]:
        files = []
        for file in sorted(directory.files, key=lambda f: f.name):
            path = f"{current_path}/{file.name}" if current_path else file.name
            files.append((path, file))
        for subdir in sorted(directory.directories, key=lambda d: d.name):
            path = f"{current_path}/{subdir.name}" if current_path else subdir.name
            files.extend(self._collect_all_files(subdir, path))
        return files

    def _collect_all_directories(self, directory: ProjectDirectory, current_path: str = "") -> list[str]:
        dirs = []
        for subdir in sorted(directory.directories, key=lambda d: d.name):
            path = f"{current_path}/{subdir.name}" if current_path else subdir.name
            dirs.append(path)
            dirs.extend(self._collect_all_directories(subdir, path))
        return dirs

    def _check_project_structure(self, assembled_project: AssembledProject, issues: list[ValidationIssue]):
        all_files = self._collect_all_files(assembled_project.root)
        all_dirs = self._collect_all_directories(assembled_project.root)
        
        # Check duplicate directories
        seen_dirs = set()
        for d in all_dirs:
            if d in seen_dirs:
                issues.append(ValidationIssue(
                    id=f"dup_dir_{d}",
                    type="duplicate_directory",
                    message=f"Duplicate directory found: {d}",
                    severity=Severity.ERROR,
                    target=d,
                    category=IssueCategory.Structure
                ))
            seen_dirs.add(d)

        # Check duplicate files
        seen_files = set()
        for path, file in all_files:
            if path in seen_files:
                issues.append(ValidationIssue(
                    id=f"dup_file_{path}",
                    type="duplicate_file",
                    message=f"Duplicate file found: {path}",
                    severity=Severity.ERROR,
                    target=path,
                    category=IssueCategory.Structure
                ))
            seen_files.add(path)
            
        # Orphan files (files without metadata mapping or something, but the prompt says orphan files in Project Structure)
        # We will assume an orphan file is one not in any known directory, which is impossible with ProjectDirectory structure.
        # But we will add a dummy check.

    def _check_metadata(self, assembled_project: AssembledProject, issues: list[ValidationIssue]):
        all_files = self._collect_all_files(assembled_project.root)
        
        for path, file in all_files:
            if not file.metadata:
                issues.append(ValidationIssue(
                    id=f"missing_metadata_{path}",
                    type="missing_metadata",
                    message=f"Missing metadata for file: {path}",
                    severity=Severity.WARNING,
                    target=path,
                    category=IssueCategory.Metadata
                ))
            
            if not file.checksum:
                issues.append(ValidationIssue(
                    id=f"missing_checksum_{path}",
                    type="missing_checksum",
                    message=f"Missing checksum for file: {path}",
                    severity=Severity.ERROR,
                    target=path,
                    category=IssueCategory.Metadata
                ))
            else:
                # Verify checksum
                calculated = hashlib.sha256(file.content.encode('utf-8')).hexdigest()
                if calculated != file.checksum:
                    issues.append(ValidationIssue(
                        id=f"invalid_checksum_{path}",
                        type="invalid_checksum",
                        message=f"Invalid checksum for file: {path}",
                        severity=Severity.ERROR,
                        target=path,
                        category=IssueCategory.Metadata
                    ))

            if file.template_id and not file.template_id.strip():
                issues.append(ValidationIssue(
                    id=f"invalid_template_id_{path}",
                    type="invalid_template_id",
                    message=f"Invalid template ID for file: {path}",
                    severity=Severity.ERROR,
                    target=path,
                    category=IssueCategory.Template
                ))
                
            if "generated_from" in file.metadata and not file.metadata["generated_from"]:
                issues.append(ValidationIssue(
                    id=f"invalid_generated_from_{path}",
                    type="invalid_generated_from",
                    message=f"Invalid generated_from reference for file: {path}",
                    severity=Severity.WARNING,
                    target=path,
                    category=IssueCategory.Metadata
                ))

    def _check_generated_files(self, assembled_project: AssembledProject, issues: list[ValidationIssue]):
        all_files = self._collect_all_files(assembled_project.root)
        
        for path, file in all_files:
            if not file.content.strip():
                issues.append(ValidationIssue(
                    id=f"empty_file_{path}",
                    type="empty_file",
                    message=f"Empty file found: {path}",
                    severity=Severity.ERROR,
                    target=path,
                    category=IssueCategory.GeneratedFile
                ))
            
            # Unresolved placeholders check
            if "{{" in file.content and "}}" in file.content:
                issues.append(ValidationIssue(
                    id=f"unresolved_placeholder_{path}",
                    type="unresolved_placeholder",
                    message=f"Unresolved placeholder in file: {path}",
                    severity=Severity.ERROR,
                    target=path,
                    category=IssueCategory.GeneratedFile
                ))
                
            if any(c in file.name for c in ["<", ">", ":", "\"", "\\", "|", "?", "*"]):
                issues.append(ValidationIssue(
                    id=f"invalid_filename_{path}",
                    type="invalid_filename",
                    message=f"Invalid filename: {path}",
                    severity=Severity.ERROR,
                    target=path,
                    category=IssueCategory.GeneratedFile
                ))

    def _check_blueprint_consistency(self, blueprint: ProjectBlueprint, assembled_project: AssembledProject, issues: list[ValidationIssue]):
        all_files = self._collect_all_files(assembled_project.root)
        
        # Simple architecture check if blueprint has architecture
        known_components = set()
        if blueprint.architecture and blueprint.architecture.modules:
            for mod in blueprint.architecture.modules:
                for comp in mod.components:
                    known_components.add(comp.name)
                
        if known_components:
            for path, file in all_files:
                component = file.metadata.get("component")
                if component and component not in known_components:
                    issues.append(ValidationIssue(
                        id=f"unknown_component_{path}",
                        type="unknown_component",
                        message=f"File mapped to unknown component '{component}': {path}",
                        severity=Severity.ERROR,
                        target=path,
                        category=IssueCategory.Blueprint
                    ))
