import json
from typing import Dict, Any, List
from .models import Workflow

class OrchestratorExporter:
    @staticmethod
    def to_dict(workflow: Workflow) -> Dict[str, Any]:
        return workflow.model_dump(mode='json')

    @staticmethod
    def to_json(workflow: Workflow, indent: int = 2) -> str:
        return json.dumps(OrchestratorExporter.to_dict(workflow), indent=indent)

    @staticmethod
    def summary(workflow: Workflow) -> str:
        lines = [
            f"Workflow ID: {workflow.id}",
            f"Total Tasks: {len(workflow.assignments)}",
            f"Execution History Events: {len(workflow.execution_history)}"
        ]
        
        counts: Dict[str, int] = {}
        for a in workflow.assignments.values():
            counts[a.status.value] = counts.get(a.status.value, 0) + 1
            
        lines.append("Status Counts:")
        for k, v in counts.items():
            lines.append(f"  {k}: {v}")
            
        return "\n".join(lines)

    @staticmethod
    def statistics(workflow: Workflow) -> Dict[str, int]:
        stats = {
            "total_tasks": len(workflow.assignments),
            "history_events": len(workflow.execution_history)
        }
        for a in workflow.assignments.values():
            key = f"status_{a.status.value}"
            stats[key] = stats.get(key, 0) + 1
        return stats
