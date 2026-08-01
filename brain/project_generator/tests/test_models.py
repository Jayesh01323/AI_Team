from brain.project_generator.models import GeneratedFile, ProjectBlueprint, GeneratorContext, ValidationResult

def test_generated_file_creation():
    gf = GeneratedFile(path="main.py", content="print('hello')", is_executable=True)
    assert gf.path == "main.py"
    assert gf.content == "print('hello')"
    assert gf.is_executable is True

def test_project_blueprint():
    bp = ProjectBlueprint(project_name="TestApp")
    assert bp.project_name == "TestApp"
    assert bp.specification is None
    assert bp.plan is None
    assert bp.architecture is None

def test_generator_context():
    bp = ProjectBlueprint(project_name="TestApp")
    ctx = GeneratorContext(blueprint=bp, original_intent="Create an app")
    assert ctx.blueprint.project_name == "TestApp"
    assert ctx.original_intent == "Create an app"
    assert len(ctx.generated_files) == 0

def test_validation_result():
    vr = ValidationResult(is_valid=False, errors=["Error 1"])
    assert vr.is_valid is False
    assert "Error 1" in vr.errors
