from .interfaces import IProjectExporter
from .models import GeneratorContext


class ProjectExporter(IProjectExporter):
    def export(self, context: GeneratorContext, destination: str) -> None:
        # Foundation skeleton.
        pass
