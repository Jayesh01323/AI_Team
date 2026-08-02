from brain.project_generator.assembly_exporter import AssemblyExporter
from brain.project_generator.assembly_models import AssembledProject, ProjectDirectory


def test_assembly_exporter():
    exporter = AssemblyExporter()
    p = AssembledProject(project_name="Test", root=ProjectDirectory(name="root"))
    
    assert isinstance(exporter.export_dict(p), dict)
    assert isinstance(exporter.export_json(p), str)
    assert isinstance(exporter.summary(p), str)
