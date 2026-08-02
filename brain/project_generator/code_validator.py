from .code_models import CodeGenerationValidationResult, GeneratedProject


class CodeValidator:
    def validate(self, project: GeneratedProject) -> CodeGenerationValidationResult:
        errors = []
        paths = set()
        
        for file in project.generated_files:
            if file.path in paths:
                errors.append(f"Duplicate file path detected: {file.path}")
            paths.add(file.path)
            
            if not file.metadata and not isinstance(file.metadata, dict):
                errors.append(f"Missing required metadata in {file.path}")
                
            if not file.filename:
                errors.append(f"Invalid filename for {file.path}")
                
            if not file.content.strip():
                errors.append(f"Empty generated file: {file.path}")
                
            if "{{" in file.content and "}}" in file.content:
                errors.append(f"Unresolved placeholders in {file.path}")
                
        return CodeGenerationValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
