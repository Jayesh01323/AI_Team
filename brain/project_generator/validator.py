from .models import GeneratorContext, ValidationResult
from .interfaces import IProjectValidator

class ProjectValidator(IProjectValidator):
    def validate(self, context: GeneratorContext) -> ValidationResult:
        # Foundation skeleton.
        if not context.blueprint:
            return ValidationResult(is_valid=False, errors=["Missing blueprint"])
        return ValidationResult(is_valid=True)
