
from .models import AgentRegistration, AgentType


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, AgentRegistration] = {}
        
    def register_agent(self, agent: AgentRegistration) -> None:
        if agent.id in self._agents:
            raise ValueError(f"Agent with ID {agent.id} already registered.")
        self._agents[agent.id] = agent
        
    def unregister_agent(self, agent_id: str) -> None:
        if agent_id in self._agents:
            del self._agents[agent_id]
            
    def get_agent(self, agent_id: str) -> AgentRegistration | None:
        return self._agents.get(agent_id)
        
    def get_agents_by_type(self, agent_type: AgentType) -> list[AgentRegistration]:
        return [a for a in self._agents.values() if a.agent_type == agent_type]
        
    def get_all_agents(self) -> list[AgentRegistration]:
        return list(self._agents.values())
