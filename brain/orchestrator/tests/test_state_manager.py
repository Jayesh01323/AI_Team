import pytest
from brain.orchestrator.state_manager import StateManager
from brain.orchestrator.models import Workflow, TaskAssignment, AgentType, ExecutionStatus

def test_evaluate_dependencies():
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, status=ExecutionStatus.PENDING),
            "t2": TaskAssignment(task_id="t2", agent_type=AgentType.CODING, status=ExecutionStatus.PENDING, dependencies=["t1"]),
            "t3": TaskAssignment(task_id="t3", agent_type=AgentType.CODING, status=ExecutionStatus.PENDING, dependencies=["t2"])
        }
    )
    
    # t1 is ready, t2 depends on t1, so t2 is not ready. But wait, evaluate dependencies blocks t2?
    # No, evaluate dependencies doesn't block unless dependency failed. But get_ready_tasks filters it out.
    
    # Let's check get_ready_tasks
    ready = StateManager.get_ready_tasks(workflow)
    assert len(ready) == 1
    assert ready[0].task_id == "t1"
    
    # Complete t1
    StateManager.update_state(workflow, "t1", ExecutionStatus.COMPLETED)
    ready = StateManager.get_ready_tasks(workflow)
    assert len(ready) == 1
    assert ready[0].task_id == "t2"
    
    # Fail t2
    StateManager.update_state(workflow, "t2", ExecutionStatus.FAILED)
    StateManager.evaluate_dependencies(workflow)
    assert workflow.assignments["t3"].status == ExecutionStatus.BLOCKED
    ready = StateManager.get_ready_tasks(workflow)
    assert len(ready) == 0

def test_update_state_history():
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, status=ExecutionStatus.PENDING)
        }
    )
    
    StateManager.update_state(workflow, "t1", ExecutionStatus.RUNNING)
    assert workflow.assignments["t1"].status == ExecutionStatus.RUNNING
    assert len(workflow.execution_history) == 1
    assert workflow.execution_history[0]["task_id"] == "t1"
    assert workflow.execution_history[0]["new_status"] == ExecutionStatus.RUNNING.value
