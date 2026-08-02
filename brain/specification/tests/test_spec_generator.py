from brain.specification.generator import LivingSpecificationGenerator
from brain.specification.models import LivingSpecification


def test_generate_from_empty():
    spec = LivingSpecificationGenerator.generate()
    assert spec.project_name == "Unknown Project"
    assert len(spec.goals) == 0

def test_generate_from_context():
    knowledge_data = {
        "project_name": "Test Project",
        "target_users": ["User A"]
    }
    intent_data = {
        "goals": ["Goal 1"]
    }
    decision_data = {
        "accepted_decisions": []
    }
    
    spec = LivingSpecificationGenerator.generate(knowledge_data, intent_data, decision_data)
    assert spec.project_name == "Test Project"
    assert spec.target_users == ["User A"]
    assert spec.goals == ["Goal 1"]

def test_update_specification():
    current = LivingSpecification(project_name="Old")
    update = LivingSpecification(project_name="New")
    
    merged, validation = LivingSpecificationGenerator.update(current, update)
    assert merged.project_name == "New"
    assert validation.is_valid  # missing vision/problem_statement are just warnings

def test_validate():
    spec = LivingSpecification(project_name="")
    validation = LivingSpecificationGenerator.validate(spec)
    assert not validation.is_valid
