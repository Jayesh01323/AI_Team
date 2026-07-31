from typing import Dict, Any, List
from .models import Plan, Task, TaskStatus, Milestone, Epic, Feature
from .scheduler import Scheduler
from .validator import PlanValidator, ValidationResult
from .exporter import PlanExporter
from .dependency_graph import DependencyGraph
from .prioritizer import Prioritizer
from brain.specification.models import LivingSpecification

class Planner:
    """The deterministic Planner."""
    
    @staticmethod
    def generate_plan(spec: LivingSpecification) -> Plan:
        """
        Converts the Living Specification into an executable project plan.
        """
        plan = Plan(project_name=spec.project_name)
        
        # 1. Create a default Milestone
        milestone = Milestone(id="m1", title="Initial Release")
        plan.milestones.append(milestone)
        
        # 2. Map Functional Requirements to Epics/Features/Tasks
        # Simple deterministic mapping: 
        # Each Requirement becomes a Feature (in a generic Epic), with one default task.
        
        epic = Epic(id="e1", title="Core Features")
        milestone.epics.append(epic)
        
        all_tasks = []
        for req in spec.functional_requirements:
            feature = Feature(id=f"f_{req.id}", title=req.description[:50])
            epic.features.append(feature)
            
            task = Task(
                id=f"t_{req.id}",
                title=f"Implement {req.id}",
                description=req.description
            )
            feature.tasks.append(task)
            all_tasks.append(task)
            
        # Schedule the initial tasks
        if all_tasks:
            Scheduler.schedule(all_tasks)
            
        return plan

    @staticmethod
    def update_plan(current: Plan, spec: LivingSpecification) -> Plan:
        """
        Incrementally replans without destroying existing completed tasks.
        (A simplified version that respects completed tasks and re-schedules the rest).
        """
        # For simplicity, if we get a new spec, we could add new tasks.
        # Here we just re-run the scheduler on existing tasks to show incremental replanning capability.
        all_tasks = PlanExporter._get_all_tasks(current)
        Scheduler.schedule(all_tasks)
        return current
        
    @staticmethod
    def validate_plan(plan: Plan) -> ValidationResult:
        return PlanValidator.validate(plan)
        
    @staticmethod
    def calculate_priorities(tasks: List[Task]) -> None:
        Prioritizer.calculate_priorities(tasks)
        
    @staticmethod
    def build_dependency_graph(tasks: List[Task]) -> DependencyGraph:
        graph = DependencyGraph()
        graph.build_from_tasks(tasks)
        return graph
        
    @staticmethod
    def execution_order(plan: Plan) -> List[Task]:
        tasks = PlanExporter._get_all_tasks(plan)
        # Ensure they are scheduled
        Scheduler.schedule(tasks)
        return sorted(tasks, key=lambda t: t.execution_order)
        
    @staticmethod
    def ready_tasks(plan: Plan) -> List[Task]:
        return [t for t in PlanExporter._get_all_tasks(plan) if t.status == TaskStatus.READY]
        
    @staticmethod
    def blocked_tasks(plan: Plan) -> List[Task]:
        return [t for t in PlanExporter._get_all_tasks(plan) if t.status == TaskStatus.BLOCKED]
        
    @staticmethod
    def completed_tasks(plan: Plan) -> List[Task]:
        return [t for t in PlanExporter._get_all_tasks(plan) if t.status == TaskStatus.COMPLETED]
        
    @staticmethod
    def summary(plan: Plan) -> str:
        return PlanExporter.summary(plan)
        
    @staticmethod
    def statistics(plan: Plan) -> Dict[str, int]:
        return PlanExporter.statistics(plan)

