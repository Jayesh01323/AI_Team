from brain.project_generator.exporter import ProjectExporter
from brain.project_generator.models import GeneratorContext, ProjectBlueprint

def test_exporter():
    exporter = ProjectExporter()
    bp = ProjectBlueprint(project_name="TestApp")
    ctx = GeneratorContext(blueprint=bp)
    
    # Exporter does nothing in skeleton, just verify it doesn't crash
    exporter.export(ctx, "/tmp/dest")
