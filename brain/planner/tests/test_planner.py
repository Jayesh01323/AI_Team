import pytest
from brain.planner.planner import Planner
from brain.specification.models import LivingSpecification, Requirement
from brain.planner.models import TaskStatus

def test_generate_plan():
    spec = LivingSpecification(
        project_name="Planner Test",
        functional_requirements=[
            Requirement(id="req1", description="Req 1"),
            Requirement(id="req2", description="Req 2")
        ]
    )
    
    plan = Planner.generate_plan(spec)
    assert plan.project_name == "Planner Test"
    assert len(plan.milestones) == 1
    
    tasks = Planner.execution_order(plan)
    assert len(tasks) == 2
    assert tasks[0].status == TaskStatus.READY

def test_ready_and_blocked():
    spec = LivingSpecification(
        project_name="Planner Test",
        functional_requirements=[
            Requirement(id="req1", description="Req 1")
        ]
    )
    plan = Planner.generate_plan(spec)
    # By default req1 is READY
    assert len(Planner.ready_tasks(plan)) == 1
    assert len(Planner.blocked_tasks(plan)) == 0
    assert len(Planner.completed_tasks(plan)) == 0

def test_statistics_and_summary():
    spec = LivingSpecification(
        project_name="Planner Test",
        functional_requirements=[
            Requirement(id="req1", description="Req 1")
        ]
    )
    plan = Planner.generate_plan(spec)
    stats = Planner.statistics(plan)
    assert stats["total_tasks"] == 1
    
    summary = Planner.summary(plan)
    assert "Planner Test" in summary
