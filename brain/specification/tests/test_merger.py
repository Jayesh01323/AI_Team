from brain.specification.merger import merge_specifications
from brain.specification.models import (
    Decision,
    EntityStatus,
    LivingSpecification,
    Requirement,
)


def test_merge_decisions_never_silently_removes_accepted():
    d1 = Decision(id="d1", title="Use Python", description="Python 3.10+", status=EntityStatus.ACCEPTED)
    current = LivingSpecification(accepted_decisions=[d1])
    
    update = LivingSpecification(accepted_decisions=[])
    
    merged = merge_specifications(current, update)
    assert len(merged.accepted_decisions) == 1
    assert merged.accepted_decisions[0].id == "d1"
    assert merged.accepted_decisions[0].status == EntityStatus.ACCEPTED

def test_merge_decisions_updates_status():
    d1 = Decision(id="d1", title="Use Python", description="Python", status=EntityStatus.ACCEPTED)
    current = LivingSpecification(accepted_decisions=[d1])
    
    # Intentionally trying to change status implicitly to something other than rejected/superseded won't remove accepted status
    # if it doesn't explicitly mark it as superseded/rejected (handled by merger rules)
    d1_update = Decision(id="d1", title="Use Python", description="Python", status=EntityStatus.PROPOSED)
    update = LivingSpecification(accepted_decisions=[d1_update])
    
    merged = merge_specifications(current, update)
    assert merged.accepted_decisions[0].status == EntityStatus.ACCEPTED

def test_merge_string_lists_deduplicates():
    current = LivingSpecification(goals=["Goal 1", "Goal 2"])
    update = LivingSpecification(goals=["Goal 2", "Goal 3"])
    
    merged = merge_specifications(current, update)
    assert len(merged.goals) == 3
    assert merged.goals == ["Goal 1", "Goal 2", "Goal 3"]

def test_merge_requirements():
    r1 = Requirement(id="r1", description="Fast")
    r2 = Requirement(id="r2", description="Secure")
    current = LivingSpecification(functional_requirements=[r1])
    update = LivingSpecification(functional_requirements=[r2])
    
    merged = merge_specifications(current, update)
    assert len(merged.functional_requirements) == 2
    assert "r1" in [r.id for r in merged.functional_requirements]
    assert "r2" in [r.id for r in merged.functional_requirements]

def test_merge_scalar_fields_prefer_update():
    current = LivingSpecification(project_name="Old Name", confidence_score=0.5)
    update = LivingSpecification(project_name="New Name", confidence_score=0.8)
    
    merged = merge_specifications(current, update)
    assert merged.project_name == "New Name"
    assert merged.confidence_score == 0.8
