from brain.orchestrator.models import AgentRegistration, AgentType
from brain.orchestrator.orchestrator import MultiAgentOrchestrator
from brain.planner.models import Epic, Feature, Milestone, Plan, Task


def test_orchestrator_e2e():
    orchestrator = MultiAgentOrchestrator()
    
    # Register agents
    orchestrator.register_agent(AgentRegistration(id="coder", agent_type=AgentType.CODING, description=""))
    orchestrator.register_agent(AgentRegistration(id="tester", agent_type=AgentType.TEST, description=""))
    
    # Generate plan
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
    
    # Generate workflow
    workflow = orchestrator.generate_workflow(plan)
    
    # Validate workflow
    validation = orchestrator.validate_workflow(workflow)
    assert validation.is_valid
    
    # Dispatch first task
    next_tasks = orchestrator.next_tasks(workflow)
    assert next_tasks == ["t1"]
    
    dispatched = orchestrator.dispatch(workflow, max_tasks=1)
    assert len(dispatched) == 1
    assert dispatched[0] == ("t1", "coder")
    
    # Complete first task
    orchestrator.update_state(workflow, "t1", success=True)
    
    # Dispatch second task
    next_tasks = orchestrator.next_tasks(workflow)
    assert next_tasks == ["t2"]
    
    dispatched = orchestrator.dispatch(workflow, max_tasks=1)
    assert len(dispatched) == 1
    assert dispatched[0] == ("t2", "tester")
    
    # Check history
    history = orchestrator.execution_history(workflow)
    assert len(history) == 3 # t1 RUNNING, t1 COMPLETED, t2 RUNNING
