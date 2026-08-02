import pytest

from brain.orchestrator.models import AgentRegistration, AgentType
from brain.orchestrator.registry import AgentRegistry


def test_registry_add_get():
    registry = AgentRegistry()
    agent = AgentRegistration(id="a1", agent_type=AgentType.CODING, description="")
    registry.register_agent(agent)
    
    assert registry.get_agent("a1") == agent
    assert len(registry.get_all_agents()) == 1

def test_registry_duplicate():
    registry = AgentRegistry()
    agent = AgentRegistration(id="a1", agent_type=AgentType.CODING, description="")
    registry.register_agent(agent)
    
    with pytest.raises(ValueError):
        registry.register_agent(agent)

def test_registry_unregister():
    registry = AgentRegistry()
    agent = AgentRegistration(id="a1", agent_type=AgentType.CODING, description="")
    registry.register_agent(agent)
    registry.unregister_agent("a1")
    assert registry.get_agent("a1") is None

def test_registry_get_by_type():
    registry = AgentRegistry()
    registry.register_agent(AgentRegistration(id="a1", agent_type=AgentType.CODING, description=""))
    registry.register_agent(AgentRegistration(id="a2", agent_type=AgentType.TEST, description=""))
    
    coding = registry.get_agents_by_type(AgentType.CODING)
    assert len(coding) == 1
    assert coding[0].id == "a1"
