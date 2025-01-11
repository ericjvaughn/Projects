from typing import Optional
from app.core.agent_manager import AgentManager

class MessageRouter:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
    
    async def route_message(
        self,
        message: str,
        mention: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> dict:
        """
        Route a message to the appropriate agent based on mentions or content.
        
        Args:
            message: The user's message
            mention: Optional @mention to specify an agent
            session_id: Optional session ID for context tracking
        
        Returns:
            dict: Response containing agent name and message
        """
        try:
            # If there's a mention, route to the specified agent
            if mention:
                # Remove @ symbol if present
                agent_name = mention.lstrip('@').lower()
                return await self.agent_manager.process_message(message, agent_name)
            
            # Otherwise, route to the best matching agent
            return await self.agent_manager.process_message(message)
            
        except Exception as e:
            return {
                "error": f"Error routing message: {str(e)}",
                "agent": "system"
            }
