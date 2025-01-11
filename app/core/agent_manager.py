from typing import Dict, Optional
from app.agents.base_agent import BaseAgent
from app.agents.sales_agent import SalesAgent
from app.agents.strategic_agent import StrategicAgent
from app.agents.support_agent import SupportAgent
from app.agents.technical_agent import TechnicalAgent

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {
            "sales_agent": SalesAgent(),
            "strategic_agent": StrategicAgent(),
            "support_agent": SupportAgent(),
            "technical_agent": TechnicalAgent(),
        }
        
    async def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(agent_name.lower())
    
    async def get_best_agent(self, message: str) -> BaseAgent:
        """Determine the most suitable agent based on message content."""
        # Implement agent selection logic based on message content
        # This could use NLP, keyword matching, or more sophisticated routing
        scores = {
            agent_name: await agent.calculate_relevance(message)
            for agent_name, agent in self.agents.items()
        }
        best_agent = max(scores.items(), key=lambda x: x[1])[0]
        return self.agents[best_agent]
    
    async def process_message(self, message: str, agent_name: Optional[str] = None) -> dict:
        """Process a message using either a specified agent or the best-matched agent."""
        if agent_name:
            agent = await self.get_agent(agent_name)
            if not agent:
                return {"error": f"Agent '{agent_name}' not found"}
        else:
            agent = await self.get_best_agent(message)
        
        response = await agent.process_message(message)
        return {
            "agent": agent.name,
            "response": response
        }
