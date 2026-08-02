from brain.specification.models import LivingSpecification, Requirement
from brain.specification.validator import validate_specification


def test_validation_passes_on_valid_spec():
    spec = LivingSpecification(
        project_name="Valid Project",
        vision="A great vision",
        problem_statement="A problem",
        confidence_score=0.9
    )
    result = validate_specification(spec)
    assert result.is_valid

def test_validation_fails_on_missing_project_name():
    spec = LivingSpecification(project_name="")
    result = validate_specification(spec)
    assert not result.is_valid
    assert any("project_name" in err for err in result.errors)

def test_validation_warnings_on_missing_vision():
    spec = LivingSpecification(project_name="Valid Project", vision="")
    result = validate_specification(spec)
    assert result.is_valid  # Still valid, just a warning
    assert any("vision" in warn for warn in result.warnings)

def test_validation_fails_on_duplicate_requirements():
    r1 = Requirement(id="r1", description="Fast")
    r2 = Requirement(id="r1", description="Duplicate ID")
    spec = LivingSpecification(
        project_name="Valid Project",
        functional_requirements=[r1, r2]
    )
    result = validate_specification(spec)
    assert not result.is_valid
    assert any("r1" in err for err in result.errors)

def test_validation_fails_on_invalid_confidence():
    spec = LivingSpecification(
        project_name="Valid Project",
        confidence_score=1.5
    )
    result = validate_specification(spec)
    assert not result.is_valid
    assert any("confidence score" in err.lower() for err in result.errors)
