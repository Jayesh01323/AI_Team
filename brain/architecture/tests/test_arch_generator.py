import pytest
from brain.architecture.generator import ArchitectureGenerator
from brain.specification.models import LivingSpecification, Requirement
from brain.planner.models import Plan, Milestone, Epic, Feature, Task

def test_generate_architecture():
    spec = LivingSpecification(
        project_name="ArchGenTest",
        functional_requirements=[Requirement(id="req1", description="")]
    )
    plan = Plan(
        milestones=[Milestone(id="m1", title="M1", epics=[
            Epic(id="e1", title="E1", features=[
                Feature(id="f1", title="F1", tasks=[
                    Task(id="t_req1", title="T1")
                ])
            ])
        ])]
    )
    
    arch = ArchitectureGenerator.generate_architecture(spec, plan)
    
    assert arch.project_name == "ArchGenTest"
    assert len(arch.modules) == 1
    assert arch.modules[0].id == "mod_core"
    assert len(arch.modules[0].components) == 1
    
    comp = arch.modules[0].components[0]
    assert comp.id == "comp_req1"
    assert "t_req1" in comp.tasks
    
    # Verify graph can be built
    graph = ArchitectureGenerator.build_component_graph(arch)
    assert not graph.has_cycle()
    
    # Verify validation passes
    validation = ArchitectureGenerator.validate_architecture(arch)
    assert validation.is_valid
