from .models import GeneratorContext
from .interfaces import IProjectExporter

class ProjectExporter(IProjectExporter):
    def export(self, context: GeneratorContext, destination: str) -> None:
        # Foundation skeleton.
        pass
