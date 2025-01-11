from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AgentResponse(BaseModel):
    content: str
    confidence: float
    needs_rerouting: bool = False

class BaseAgent(ABC):
    def __init__(self):
        self.name = "base_agent"
        self.description = "Base agent class"
        self.capabilities = []
        self.min_confidence_threshold = 0.3
    
    @abstractmethod
    async def process_message(self, message: str, context: Optional[List[Dict]] = None) -> AgentResponse:
        """
        Process an incoming message and return a response.
        
        Args:
            message: The user's message to process
            context: Optional list of previous messages for context
            
        Returns:
            AgentResponse containing the response content, confidence level,
            and whether the message needs rerouting
        """
        pass
    
    @abstractmethod
    async def calculate_relevance(self, message: str) -> float:
        """
        Calculate how relevant this agent is for handling the given message.
        
        Args:
            message: The message to evaluate
            
        Returns:
            Float between 0 and 1 indicating relevance/confidence
        """
        pass
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "min_confidence": self.min_confidence_threshold
        }
    
    async def _check_capability_match(self, message: str) -> float:
        """
        Check how well the message matches agent capabilities.
        
        Args:
            message: The message to check
            
        Returns:
            Float between 0 and 1 indicating match strength
        """
        message = message.lower()
        matched_capabilities = sum(
            1 for cap in self.capabilities
            if any(word in message for word in cap.lower().split())
        )
        return min(1.0, matched_capabilities / len(self.capabilities))
    
    async def _should_reroute(self, confidence: float) -> bool:
        """
        Determine if a message should be rerouted based on confidence.
        
        Args:
            confidence: The confidence score for handling the message
            
        Returns:
            Boolean indicating whether to reroute
        """
        return confidence < self.min_confidence_threshold
