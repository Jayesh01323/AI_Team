from brain.project_generator.template_models import TemplateMetadata
from brain.project_generator.template_registry import TemplateRegistry


def test_template_registry():
    registry = TemplateRegistry()
    
    t1 = TemplateMetadata(id="t1", name="T1", category="base")
    t2 = TemplateMetadata(id="t2", name="T2", category="backend")
    
    registry.register_template(t1)
    registry.register_template(t2)
    
    assert registry.get_template("t1") == t1
    assert len(registry.list_templates()) == 2
    
    filtered = registry.filter_templates(lambda t: t.category == "backend")
    assert len(filtered) == 1
    assert filtered[0].id == "t2"
    
    registry.unregister_template("t1")
    assert registry.get_template("t1") is None
    assert len(registry.list_templates()) == 1
