from brain.project_generator.models import GeneratorContext, ProjectBlueprint
from brain.project_generator.validator import ProjectValidator


def test_validator():
    validator = ProjectValidator()
    bp = ProjectBlueprint(project_name="TestApp")
    ctx = GeneratorContext(blueprint=bp)
    
    result = validator.validate(ctx)
    assert result.is_valid is True
