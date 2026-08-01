from typing import Dict, Any, List, Tuple, Optional
from brain.planner.models import Plan
from .models import AgentRegistration, Workflow, ValidationResult, ExecutionStatus
from .registry import AgentRegistry
from .workflow import WorkflowGenerator
from .dispatcher import Dispatcher
from .state_manager import StateManager
from .validator import OrchestratorValidator
from .exporter import OrchestratorExporter

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

    def dispatch(self, workflow: Workflow, max_tasks: int = 1) -> List[Tuple[str, str]]:
        return self.dispatcher.dispatch(workflow, max_tasks)

    def next_tasks(self, workflow: Workflow) -> List[str]:
        StateManager.evaluate_dependencies(workflow)
        return [a.task_id for a in StateManager.get_ready_tasks(workflow)]

    def update_state(self, workflow: Workflow, task_id: str, success: bool, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> None:
        self.dispatcher.handle_result(workflow, task_id, success, result, error)
        
    def execution_history(self, workflow: Workflow) -> List[Dict[str, Any]]:
        return workflow.execution_history
        
    def validate_workflow(self, workflow: Workflow) -> ValidationResult:
        return OrchestratorValidator.validate_workflow(workflow, self.registry)
        
    def export_dict(self, workflow: Workflow) -> Dict[str, Any]:
        return OrchestratorExporter.to_dict(workflow)
        
    def export_json(self, workflow: Workflow, indent: int = 2) -> str:
        return OrchestratorExporter.to_json(workflow, indent)
        
    def summary(self, workflow: Workflow) -> str:
        return OrchestratorExporter.summary(workflow)
        
    def statistics(self, workflow: Workflow) -> Dict[str, int]:
        return OrchestratorExporter.statistics(workflow)
