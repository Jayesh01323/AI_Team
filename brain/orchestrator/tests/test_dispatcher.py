import pytest
from brain.orchestrator.dispatcher import Dispatcher
from brain.orchestrator.registry import AgentRegistry
from brain.orchestrator.models import Workflow, TaskAssignment, AgentType, ExecutionStatus, AgentRegistration

def test_dispatch_tasks():
    registry = AgentRegistry()
    registry.register_agent(AgentRegistration(id="a1", agent_type=AgentType.CODING, description=""))
    
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, status=ExecutionStatus.PENDING),
            "t2": TaskAssignment(task_id="t2", agent_type=AgentType.TEST, status=ExecutionStatus.PENDING)
        }
    )
    
    dispatcher = Dispatcher(registry)
    
    # Try to dispatch 2 tasks. t1 should dispatch to a1. t2 should fail because no test agent.
    dispatched = dispatcher.dispatch(workflow, max_tasks=2)
    
    assert len(dispatched) == 1
    assert dispatched[0] == ("t1", "a1")
    assert workflow.assignments["t1"].status == ExecutionStatus.RUNNING
    assert workflow.assignments["t2"].status == ExecutionStatus.FAILED
    assert "No agent found" in workflow.assignments["t2"].error_message

def test_handle_result():
    registry = AgentRegistry()
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, status=ExecutionStatus.RUNNING)
        }
    )
    dispatcher = Dispatcher(registry)
    
    # Success
    dispatcher.handle_result(workflow, "t1", success=True, result={"x": 1})
    assert workflow.assignments["t1"].status == ExecutionStatus.COMPLETED
    assert workflow.assignments["t1"].execution_result == {"x": 1}

def test_handle_result_retry():
    registry = AgentRegistry()
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, status=ExecutionStatus.RUNNING, max_retries=2)
        }
    )
    dispatcher = Dispatcher(registry)
    
    # Fail once, should retry
    dispatcher.handle_result(workflow, "t1", success=False, error="Error")
    assert workflow.assignments["t1"].status == ExecutionStatus.PENDING
    assert workflow.assignments["t1"].retry_count == 1
    
    # Fail twice, should fail permanently
    workflow.assignments["t1"].status = ExecutionStatus.RUNNING
    dispatcher.handle_result(workflow, "t1", success=False, error="Error 2")
    assert workflow.assignments["t1"].status == ExecutionStatus.FAILED
    assert workflow.assignments["t1"].retry_count == 2
