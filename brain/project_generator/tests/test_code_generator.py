from brain.project_generator.code_generator import CodeGenerator
from brain.project_generator.models import ProjectBlueprint
from brain.project_generator.template_models import ResolvedTemplateSet, TemplateMetadata

def test_code_generator():
    generator = CodeGenerator()
    bp = ProjectBlueprint(project_name="MyTestProject")
    
    t1 = TemplateMetadata(id="t1", name="T1", category="base")
    t2 = TemplateMetadata(id="t2", name="T2", category="app")
    
    templates = ResolvedTemplateSet(
        selected_templates=[t1, t2],
        dependency_ordering=["t1", "t2"]
    )
    
    project = generator.generate(bp, templates)
    
    assert len(project.generated_files) == 2
    
    f1 = project.generated_files[0]
    assert f1.path == "src/t1/main.py"
    assert "MyTestProject" in f1.content
    assert "T1" in f1.content
    assert f1.checksum != ""
    
    f2 = project.generated_files[1]
    assert f2.path == "src/t2/main.py"
    assert "MyTestProject" in f2.content
    
    assert project.validation_result is not None
    assert project.validation_result.is_valid is True
