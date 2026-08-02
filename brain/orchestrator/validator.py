from .models import ValidationResult, Workflow
from .registry import AgentRegistry


class OrchestratorValidator:
    @staticmethod
    def validate_workflow(workflow: Workflow, registry: AgentRegistry) -> ValidationResult:
        result = ValidationResult()

        # Check for duplicate tasks
        task_ids = set()
        for t_id, assignment in workflow.assignments.items():
            if t_id in task_ids:
                result.is_valid = False
                result.errors.append(f"Duplicate task assignment for {t_id}")
            task_ids.add(t_id)

        # Check dependency violations and cycles
        graph = {}
        for t_id, assignment in workflow.assignments.items():
            graph[t_id] = assignment.dependencies
            for dep in assignment.dependencies:
                if dep not in workflow.assignments:
                    result.is_valid = False
                    result.errors.append(f"Task {t_id} depends on unknown task {dep}")

        # Cycle detection
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if dfs(node):
                    result.is_valid = False
                    result.errors.append("Circular dependency detected in workflow")
                    break

        # Check for required agents
        required_types = set(a.agent_type for a in workflow.assignments.values())
        for req_type in required_types:
            if not registry.get_agents_by_type(req_type):
                result.is_valid = False
                result.errors.append(f"No agents registered for required type {req_type}")

        return result
