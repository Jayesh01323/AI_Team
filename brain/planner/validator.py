from typing import Any

from .dependency_graph import DependencyGraph
from .models import Plan


class ValidationResult:
    def __init__(self):
        self.is_valid: bool = True
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

class PlanValidator:
    @staticmethod
    def validate(plan: Plan) -> ValidationResult:
        result = ValidationResult()

        task_ids = set()
        tasks = []
        
        # Check duplicate IDs and gather tasks
        for milestone in plan.milestones:
            for epic in milestone.epics:
                for feature in epic.features:
                    for task in feature.tasks:
                        if task.id in task_ids:
                            result.add_error(f"Duplicate task ID found: {task.id}")
                        task_ids.add(task.id)
                        tasks.append(task)
                        
                        # Validate priority values
                        if task.priority_score < 0:
                            result.add_error(f"Invalid priority score for task {task.id}: {task.priority_score}")
                            
        # Dependency graph checks
        graph = DependencyGraph()
        try:
            graph.build_from_tasks(tasks)
        except Exception as e:
            result.add_error(f"Failed to build dependency graph: {e!s}")
            
        if graph.has_cycle():
            result.add_error("Dependency cycle detected in plan")
            
        # Check execution order (should be >= 0 if scheduled)
        for task in tasks:
            if task.execution_order < 0:
                result.add_warning(f"Task {task.id} has not been scheduled (execution_order < 0)")
            for dep in task.dependencies:
                if dep not in task_ids:
                    result.add_error(f"Task {task.id} depends on unknown task {dep}")

        return result
