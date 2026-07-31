from typing import Dict, Any, List
from .models import Workflow, ExecutionStatus, TaskAssignment
import time

class StateManager:
    @staticmethod
    def update_state(workflow: Workflow, task_id: str, new_status: ExecutionStatus, result: Dict[str, Any] = None, error: str = None) -> None:
        if task_id not in workflow.assignments:
            raise ValueError(f"Task {task_id} not found in workflow")
            
        assignment = workflow.assignments[task_id]
        old_status = assignment.status
        assignment.status = new_status
        
        if result:
            assignment.execution_result = result
        if error:
            assignment.error_message = error
            
        # Record history
        workflow.execution_history.append({
            "task_id": task_id,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "timestamp": time.time(),
            "error": error
        })
        
    @staticmethod
    def evaluate_dependencies(workflow: Workflow) -> None:
        """
        Updates task statuses based on their dependencies.
        If a pending task has all dependencies completed, it stays pending (ready to run).
        If a dependency is failed, the task should be blocked.
        """
        for task_id, assignment in workflow.assignments.items():
            if assignment.status in (ExecutionStatus.PENDING, ExecutionStatus.BLOCKED):
                # Check dependencies
                all_completed = True
                any_failed = False
                
                for dep_id in assignment.dependencies:
                    if dep_id in workflow.assignments:
                        dep_status = workflow.assignments[dep_id].status
                        if dep_status == ExecutionStatus.FAILED:
                            any_failed = True
                        elif dep_status != ExecutionStatus.COMPLETED:
                            all_completed = False
                            
                if any_failed:
                    if assignment.status != ExecutionStatus.BLOCKED:
                        StateManager.update_state(workflow, task_id, ExecutionStatus.BLOCKED, error="Dependencies failed")
                elif all_completed and assignment.status == ExecutionStatus.BLOCKED:
                    StateManager.update_state(workflow, task_id, ExecutionStatus.PENDING)

    @staticmethod
    def get_ready_tasks(workflow: Workflow) -> List[TaskAssignment]:
        ready_tasks = []
        for task_id, assignment in workflow.assignments.items():
            if assignment.status == ExecutionStatus.PENDING:
                # Double check dependencies
                ready = True
                for dep_id in assignment.dependencies:
                    if dep_id in workflow.assignments and workflow.assignments[dep_id].status != ExecutionStatus.COMPLETED:
                        ready = False
                        break
                if ready:
                    ready_tasks.append(assignment)
        return ready_tasks
