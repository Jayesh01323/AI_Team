from brain.project_generator.generator import ProjectGenerator
from brain.project_generator.models import GeneratorContext, ProjectBlueprint

def test_generator_initialization():
    gen = ProjectGenerator()
    assert gen is not None

def test_generator_generate():
    gen = ProjectGenerator()
    bp = ProjectBlueprint(project_name="TestApp")
    ctx = GeneratorContext(blueprint=bp)
    
    result = gen.generate(ctx)
    assert result == ctx
