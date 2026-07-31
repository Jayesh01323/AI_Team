import json
from typing import Dict, Any, List
from .models import Plan, Task, TaskStatus

class PlanExporter:
    @staticmethod
    def to_dict(plan: Plan) -> Dict[str, Any]:
        return plan.model_dump(mode='json')

    @staticmethod
    def to_json(plan: Plan, indent: int = 2) -> str:
        return json.dumps(PlanExporter.to_dict(plan), indent=indent)

    @staticmethod
    def summary(plan: Plan) -> str:
        all_tasks = PlanExporter._get_all_tasks(plan)
        completed = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
        total = len(all_tasks)
        
        lines = [
            f"Plan for: {plan.project_name}",
            f"Milestones: {len(plan.milestones)}",
            f"Total Tasks: {total}",
            f"Completed Tasks: {completed}",
            f"Progress: {(completed/total*100) if total > 0 else 0:.1f}%",
            f"Last Updated: {plan.last_updated.isoformat()}"
        ]
        return "\n".join(lines)

    @staticmethod
    def statistics(plan: Plan) -> Dict[str, int]:
        all_tasks = PlanExporter._get_all_tasks(plan)
        return {
            "total_milestones": len(plan.milestones),
            "total_epics": sum(len(m.epics) for m in plan.milestones),
            "total_features": sum(len(e.features) for m in plan.milestones for e in m.epics),
            "total_tasks": len(all_tasks),
            "completed_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED),
            "ready_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.READY),
            "blocked_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.BLOCKED),
            "backlog_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.BACKLOG)
        }
        
    @staticmethod
    def _get_all_tasks(plan: Plan) -> List[Task]:
        tasks = []
        for milestone in plan.milestones:
            for epic in milestone.epics:
                for feature in epic.features:
                    tasks.extend(feature.tasks)
        return tasks
