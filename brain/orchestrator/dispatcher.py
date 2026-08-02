from typing import Any

from .models import ExecutionStatus, Workflow
from .registry import AgentRegistry
from .state_manager import StateManager


class Dispatcher:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def dispatch(self, workflow: Workflow, max_tasks: int = 1) -> list[tuple[str, str]]:
        """
        Dispatches ready tasks to agents.
        Returns a list of tuples (task_id, assigned_agent_id).
        """
        StateManager.evaluate_dependencies(workflow)
        ready_tasks = StateManager.get_ready_tasks(workflow)
        
        dispatched = []
        for assignment in ready_tasks[:max_tasks]:
            # Find an agent of the right type
            agents = self.registry.get_agents_by_type(assignment.agent_type)
            if not agents:
                StateManager.update_state(
                    workflow, 
                    assignment.task_id, 
                    ExecutionStatus.FAILED, 
                    error=f"No agent found for type {assignment.agent_type}"
                )
                continue
                
            # For simplicity, assign to the first available agent
            agent = agents[0]
            
            # Transition to RUNNING
            StateManager.update_state(workflow, assignment.task_id, ExecutionStatus.RUNNING)
            dispatched.append((assignment.task_id, agent.id))
            
        return dispatched

    def handle_result(self, workflow: Workflow, task_id: str, success: bool, result: dict[str, Any] | None = None, error: str | None = None) -> None:
        if task_id not in workflow.assignments:
            raise ValueError(f"Unknown task {task_id}")
            
        assignment = workflow.assignments[task_id]
        if assignment.status != ExecutionStatus.RUNNING:
            raise ValueError(f"Task {task_id} is not running")
            
        if success:
            StateManager.update_state(workflow, task_id, ExecutionStatus.COMPLETED, result=result)
        else:
            assignment.retry_count += 1
            if assignment.retry_count >= assignment.max_retries:
                StateManager.update_state(workflow, task_id, ExecutionStatus.FAILED, error=error)
            else:
                # Retry
                StateManager.update_state(workflow, task_id, ExecutionStatus.PENDING, error=error)
