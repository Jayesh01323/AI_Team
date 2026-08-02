from brain.orchestrator.models import (
    AgentRegistration,
    AgentType,
    TaskAssignment,
    Workflow,
)
from brain.orchestrator.registry import AgentRegistry
from brain.orchestrator.validator import OrchestratorValidator


def test_validate_valid_workflow():
    registry = AgentRegistry()
    registry.register_agent(AgentRegistration(id="a1", agent_type=AgentType.CODING, description=""))
    
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING)
        }
    )
    
    result = OrchestratorValidator.validate_workflow(workflow, registry)
    assert result.is_valid

def test_validate_missing_agent():
    registry = AgentRegistry()
    # Missing TEST agent
    
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.TEST)
        }
    )
    
    result = OrchestratorValidator.validate_workflow(workflow, registry)
    assert not result.is_valid
    assert any("No agents registered" in e for e in result.errors)

def test_validate_circular_dependency():
    registry = AgentRegistry()
    registry.register_agent(AgentRegistration(id="a1", agent_type=AgentType.CODING, description=""))
    
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, dependencies=["t2"]),
            "t2": TaskAssignment(task_id="t2", agent_type=AgentType.CODING, dependencies=["t1"])
        }
    )
    
    result = OrchestratorValidator.validate_workflow(workflow, registry)
    assert not result.is_valid
    assert any("Circular dependency" in e for e in result.errors)

def test_validate_unknown_dependency():
    registry = AgentRegistry()
    registry.register_agent(AgentRegistration(id="a1", agent_type=AgentType.CODING, description=""))
    
    workflow = Workflow(
        id="w1",
        assignments={
            "t1": TaskAssignment(task_id="t1", agent_type=AgentType.CODING, dependencies=["t_unknown"])
        }
    )
    
    result = OrchestratorValidator.validate_workflow(workflow, registry)
    assert not result.is_valid
    assert any("unknown task t_unknown" in e for e in result.errors)
