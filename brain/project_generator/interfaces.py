from abc import ABC, abstractmethod

from .models import GeneratorContext, ValidationResult


class IProjectGenerator(ABC):
    @abstractmethod
    def generate(self, context: GeneratorContext) -> GeneratorContext:
        pass

class IProjectValidator(ABC):
    @abstractmethod
    def validate(self, context: GeneratorContext) -> ValidationResult:
        pass

class IProjectExporter(ABC):
    @abstractmethod
    def export(self, context: GeneratorContext, destination: str) -> None:
        pass
