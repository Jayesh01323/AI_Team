import pytest
from brain.architecture.mapper import ArchitectureMapper
from brain.architecture.models import Architecture, Module
from brain.specification.models import LivingSpecification, Requirement
from brain.planner.models import Plan, Milestone, Epic, Feature, Task

def test_map_requirements():
    spec = LivingSpecification(
        project_name="Test",
        functional_requirements=[Requirement(id="req1", description="Test req")]
    )
    arch = Architecture()
    
    ArchitectureMapper.map_requirements_to_components(spec, arch)
    
    # Expects a core module with one component
    assert len(arch.modules) == 1
    assert arch.modules[0].id == "mod_core"
    assert len(arch.modules[0].components) == 1
    assert arch.modules[0].components[0].id == "comp_req1"
    
    assert len(arch.traceability_links) == 1
    assert arch.traceability_links[0].source_id == "req1"

def test_map_tasks():
    # Setup architecture with a component
    arch = Architecture()
    mod = Module(id="mod_core", name="Core")
    from brain.architecture.models import Component
    mod.components.append(Component(id="comp_req1", name="Req 1", description=""))
    arch.modules.append(mod)
    
    # Setup plan with a task
    plan = Plan(
        milestones=[Milestone(id="m1", title="M1", epics=[
            Epic(id="e1", title="E1", features=[
                Feature(id="f1", title="F1", tasks=[
                    Task(id="t_req1", title="T1")
                ])
            ])
        ])]
    )
    
    ArchitectureMapper.map_tasks_to_components(plan, arch)
    
    assert "t_req1" in arch.modules[0].components[0].tasks
    assert any(link.source_id == "t_req1" for link in arch.traceability_links)

def test_map_technology():
    spec = LivingSpecification(
        project_name="Test",
        technology_stack={"backend": "Python"}
    )
    arch = Architecture()
    ArchitectureMapper.map_technology(spec, arch)
    assert arch.technology_mapping["backend"] == "Python"
