from brain.orchestrator.models import AgentType, ExecutionStatus
from brain.orchestrator.workflow import WorkflowGenerator
from brain.planner.models import Epic, Feature, Milestone, Plan, Task


def test_workflow_generation():
    plan = Plan(
        milestones=[Milestone(id="m1", title="M1", epics=[
            Epic(id="e1", title="E1", features=[
                Feature(id="f1", title="F1", tasks=[
                    Task(id="t1", title="Implement feature", dependencies=[]),
                    Task(id="t2", title="Write tests", dependencies=["t1"])
                ])
            ])
        ])]
    )
    
    workflow = WorkflowGenerator.generate_workflow(plan)
    
    assert len(workflow.assignments) == 2
    assert workflow.assignments["t1"].agent_type == AgentType.CODING
    assert workflow.assignments["t2"].agent_type == AgentType.TEST
    
    assert workflow.assignments["t1"].status == ExecutionStatus.PENDING
    assert workflow.assignments["t2"].dependencies == ["t1"]
