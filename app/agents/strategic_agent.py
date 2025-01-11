from typing import List, Dict, Optional
from app.agents.base_agent import BaseAgent, AgentResponse

class StrategicAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "strategic_agent"
        self.description = "Strategic planning and business strategy specialist"
        self.capabilities = [
            "business strategy",
            "market analysis",
            "competitive analysis",
            "growth planning",
            "risk assessment"
        ]
        
        self.keywords = [
            "strategy", "plan", "market", "growth", "competition",
            "risk", "opportunity", "analysis", "forecast", "trend",
            "swot", "vision", "mission", "objective", "goal"
        ]
        
        self.min_confidence_threshold = 0.4
    
    async def calculate_relevance(self, message: str) -> float:
        """Calculate relevance score for strategic queries."""
        message = message.lower()
        
        # Check keyword matches
        keyword_matches = sum(1 for keyword in self.keywords if keyword in message)
        keyword_score = min(1.0, keyword_matches / 3)
        
        # Check capability matches
        capability_score = await self._check_capability_match(message)
        
        # Combine scores with weights
        final_score = (keyword_score * 0.7) + (capability_score * 0.3)
        return final_score
    
    async def process_message(self, message: str, context: Optional[List[Dict]] = None) -> AgentResponse:
        """Process strategy-related queries with context awareness."""
        message = message.lower()
        confidence = await self.calculate_relevance(message)
        
        # Check if we should handle this message
        if await self._should_reroute(confidence):
            return AgentResponse(
                content="I'm not confident I can provide the best response to this query.",
                confidence=confidence,
                needs_rerouting=True
            )
        
        # Consider context if available
        context_keywords = set()
        if context:
            context_text = " ".join([msg["message"].lower() for msg in context])
            context_keywords = {word for word in self.keywords if word in context_text}
        
        # Generate response based on message content
        response_content = await self._generate_strategic_response(message, context_keywords)
        
        return AgentResponse(
            content=response_content,
            confidence=confidence,
            needs_rerouting=False
        )
    
    async def _generate_strategic_response(self, message: str, context_keywords: set) -> str:
        """Generate appropriate strategic response based on message and context."""
        # Handle different types of strategic queries
        if any(word in message for word in ["market", "competition"]):
            return "I can help analyze market conditions and competitive landscape. Would you like a specific market analysis or competitor comparison?"
        
        elif any(word in message for word in ["risk", "swot"]):
            return "I can assist with risk assessment and SWOT analysis. What specific aspects would you like to evaluate?"
        
        elif any(word in message for word in ["growth", "opportunity"]):
            return "Let's explore growth opportunities. I can help identify market gaps, expansion strategies, and potential opportunities."
        
        elif any(word in message for word in ["plan", "objective", "goal"]):
            return "I'll help you develop strategic plans and objectives. Would you like to focus on short-term or long-term planning?"
        
        # Consider context for more nuanced responses
        if context_keywords:
            return f"Based on our discussion about {', '.join(context_keywords)}, how can I help with your strategic planning needs?"
        
        return "I'm your strategic planning assistant. I can help with market analysis, risk assessment, growth planning, and competitive strategy. What would you like to focus on?"
