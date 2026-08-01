from .models import GeneratorContext
from .interfaces import IProjectGenerator

class ProjectGenerator(IProjectGenerator):
    """
    Core project generator.
    Foundation only: does not generate project files yet.
    """
    def __init__(self):
        pass
        
    def generate(self, context: GeneratorContext) -> GeneratorContext:
        # Foundation skeleton. Currently a no-op.
        return context
