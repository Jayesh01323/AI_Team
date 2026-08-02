from typing import Any

from brain.planner.models import Plan

from .dispatcher import Dispatcher
from .exporter import OrchestratorExporter
from .models import AgentRegistration, ValidationResult, Workflow
from .registry import AgentRegistry
from .state_manager import StateManager
from .validator import OrchestratorValidator
from .workflow import WorkflowGenerator


class MultiAgentOrchestrator:
    def __init__(self):
        self.registry = AgentRegistry()
        self.dispatcher = Dispatcher(self.registry)

    def register_agent(self, agent: AgentRegistration) -> None:
        self.registry.register_agent(agent)
        
    def unregister_agent(self, agent_id: str) -> None:
        self.registry.unregister_agent(agent_id)

    def generate_workflow(self, plan: Plan) -> Workflow:
        return WorkflowGenerator.generate_workflow(plan)

    def dispatch(self, workflow: Workflow, max_tasks: int = 1) -> list[tuple[str, str]]:
        return self.dispatcher.dispatch(workflow, max_tasks)

    def next_tasks(self, workflow: Workflow) -> list[str]:
        StateManager.evaluate_dependencies(workflow)
        return [a.task_id for a in StateManager.get_ready_tasks(workflow)]

    def update_state(self, workflow: Workflow, task_id: str, success: bool, result: dict[str, Any] | None = None, error: str | None = None) -> None:
        self.dispatcher.handle_result(workflow, task_id, success, result, error)
        
    def execution_history(self, workflow: Workflow) -> list[dict[str, Any]]:
        return workflow.execution_history
        
    def validate_workflow(self, workflow: Workflow) -> ValidationResult:
        return OrchestratorValidator.validate_workflow(workflow, self.registry)
        
    def export_dict(self, workflow: Workflow) -> dict[str, Any]:
        return OrchestratorExporter.to_dict(workflow)
        
    def export_json(self, workflow: Workflow, indent: int = 2) -> str:
        return OrchestratorExporter.to_json(workflow, indent)
        
    def summary(self, workflow: Workflow) -> str:
        return OrchestratorExporter.summary(workflow)
        
    def statistics(self, workflow: Workflow) -> dict[str, int]:
        return OrchestratorExporter.statistics(workflow)
