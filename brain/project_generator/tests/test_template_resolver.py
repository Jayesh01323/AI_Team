from brain.project_generator.models import ProjectBlueprint
from brain.project_generator.template_models import TemplateMetadata
from brain.project_generator.template_registry import TemplateRegistry
from brain.project_generator.template_resolver import TemplateResolver


def test_template_resolver_dependencies():
    registry = TemplateRegistry()
    # t1 depends on t2
    t1 = TemplateMetadata(id="t1", name="T1", category="app", dependencies=["t2"])
    t2 = TemplateMetadata(id="t2", name="T2", category="base")
    
    registry.register_template(t1)
    registry.register_template(t2)
    
    resolver = TemplateResolver(registry)
    bp = ProjectBlueprint(project_name="TestApp")
    
    result = resolver.resolve_templates(bp)
    
    assert result.validation_result.is_valid is True
    # Dependency ordering should put t2 before t1
    assert result.dependency_ordering == ["t2", "t1"]

def test_template_resolver_missing_dependency():
    registry = TemplateRegistry()
    t1 = TemplateMetadata(id="t1", name="T1", category="app", dependencies=["t2"])
    registry.register_template(t1)
    
    resolver = TemplateResolver(registry)
    bp = ProjectBlueprint(project_name="TestApp")
    
    result = resolver.resolve_templates(bp)
    assert result.validation_result.is_valid is False
    assert any("Missing required template" in e for e in result.validation_result.errors)

def test_template_resolver_circular_dependency():
    registry = TemplateRegistry()
    t1 = TemplateMetadata(id="t1", name="T1", category="app", dependencies=["t2"])
    t2 = TemplateMetadata(id="t2", name="T2", category="app", dependencies=["t1"])
    registry.register_template(t1)
    registry.register_template(t2)
    
    resolver = TemplateResolver(registry)
    bp = ProjectBlueprint(project_name="TestApp")
    
    result = resolver.resolve_templates(bp)
    assert result.validation_result.is_valid is False
    assert any("Circular dependency" in e for e in result.validation_result.errors)

def test_template_resolver_conflicts():
    registry = TemplateRegistry()
    t1 = TemplateMetadata(id="t1", name="T1", category="backend_framework")
    t2 = TemplateMetadata(id="t2", name="T2", category="backend_framework")
    registry.register_template(t1)
    registry.register_template(t2)
    
    resolver = TemplateResolver(registry)
    bp = ProjectBlueprint(project_name="TestApp")
    
    result = resolver.resolve_templates(bp)
    assert result.validation_result.is_valid is False
    assert any("Incompatible combination" in e for e in result.validation_result.errors)
