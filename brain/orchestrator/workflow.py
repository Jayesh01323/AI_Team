from typing import Dict, List, Optional
from brain.planner.models import Plan, Task as PlanTask
from .models import Workflow, TaskAssignment, AgentType, ExecutionStatus

class WorkflowGenerator:
    @staticmethod
    def _determine_agent(task: PlanTask) -> AgentType:
        # A simple heuristic to map tasks to agent types deterministically
        title_lower = task.title.lower()
        if "design" in title_lower or "architecture" in title_lower:
            return AgentType.ARCHITECT
        elif "test" in title_lower:
            return AgentType.TEST
        elif "doc" in title_lower:
            return AgentType.DOCUMENTATION
        elif "review" in title_lower:
            return AgentType.REVIEW
        else:
            return AgentType.CODING

    @staticmethod
    def generate_workflow(plan: Plan) -> Workflow:
        workflow = Workflow(id=f"wf_{id(plan)}")
        
        # Flatten all tasks from the plan
        all_tasks = []
        for m in plan.milestones:
            for e in m.epics:
                for f in e.features:
                    for t in f.tasks:
                        all_tasks.append(t)
                        
        for task in all_tasks:
            agent_type = WorkflowGenerator._determine_agent(task)
            
            assignment = TaskAssignment(
                task_id=task.id,
                agent_type=agent_type,
                status=ExecutionStatus.PENDING,
                dependencies=task.dependencies.copy()
            )
            workflow.assignments[task.id] = assignment
            
        return workflow
