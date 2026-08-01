from brain.project_generator.template_registry import TemplateRegistry
from brain.project_generator.template_models import TemplateMetadata
from brain.project_generator.template_matcher import TemplateMatcher
from brain.project_generator.models import ProjectBlueprint
from brain.architecture.models import Architecture

def test_template_matcher():
    registry = TemplateRegistry()
    t1 = TemplateMetadata(id="t1", name="T1", category="base", priority=10)
    t2 = TemplateMetadata(id="t2", name="T2", category="backend", supported_backends=["fastapi"], priority=20)
    t3 = TemplateMetadata(id="t3", name="T3", category="backend", supported_backends=["django"], priority=5)
    
    registry.register_template(t1)
    registry.register_template(t2)
    registry.register_template(t3)
    
    matcher = TemplateMatcher(registry)
    
    # Blueprint with fastapi
    arch = Architecture(project_name="sys", technology_mapping={"backend": "fastapi"})
    bp = ProjectBlueprint(project_name="TestApp", architecture=arch)
    
    matched = matcher.match(bp)
    
    # Should match t1 (supports all) and t2 (supports fastapi)
    # Priority sorting means t2 (20) comes before t1 (10)
    assert len(matched) == 2
    assert matched[0].id == "t2"
    assert matched[1].id == "t1"
