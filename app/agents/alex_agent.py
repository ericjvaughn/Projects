from typing import List, Dict, Optional
from app.agents.base_agent import BaseAgent, AgentResponse

class AlexAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "alex"
        self.description = "General chat and coordination agent"
        self.capabilities = [
            "general conversation",
            "task coordination",
            "agent delegation",
            "information synthesis",
            "clarification questions",
            "follow-up management"
        ]
        
        self.keywords = [
            "help", "hello", "hi", "hey", "general",
            "question", "explain", "understand", "coordinate",
            "overview", "summary", "synthesize", "combine",
            "clarify", "follow up", "status"
        ]
        
        # Lower threshold as general agent
        self.min_confidence_threshold = 0.2
    
    async def calculate_relevance(self, message: str) -> float:
        """Calculate relevance for general queries."""
        message = message.lower()
        
        # Always maintain a base relevance as the general agent
        base_relevance = 0.2
        
        # Check keyword matches
        keyword_matches = sum(1 for keyword in self.keywords if keyword in message)
        keyword_score = min(1.0, keyword_matches / 2)
        
        # Check capability matches
        capability_score = await self._check_capability_match(message)
        
        # Combine scores with weights, including base relevance
        final_score = (
            (keyword_score * 0.4) +
            (capability_score * 0.3) +
            base_relevance
        )
        return min(1.0, final_score)
    
    async def process_message(self, message: str, context: Optional[List[Dict]] = None) -> AgentResponse:
        """Process general queries and coordinate with other agents."""
        message = message.lower()
        confidence = await self.calculate_relevance(message)
        
        # Generate appropriate response
        response_content = await self._generate_response(message, context)
        
        return AgentResponse(
            content=response_content,
            confidence=confidence,
            needs_rerouting=False  # General agent doesn't reroute
        )
    
    async def _generate_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Generate contextual responses for general queries."""
        # Greeting patterns
        if any(word in message for word in ["hello", "hi", "hey"]):
            return "Hello! I'm ALEX, your general assistant. How can I help you today?"
        
        # Help or guidance requests
        if "help" in message:
            return ("I can help you with various tasks or connect you with specialized agents:\n"
                   "- @marketing for marketing strategies\n"
                   "- @sales for sales inquiries\n"
                   "- @growth for growth initiatives\n"
                   "- @brand for brand management\n"
                   "What would you like to know more about?")
        
        # Clarification requests
        if any(word in message for word in ["explain", "clarify", "understand"]):
            return "I'll help clarify that for you. Could you tell me which specific aspect you'd like me to explain?"
        
        # Status or follow-up requests
        if any(word in message for word in ["status", "follow", "update"]):
            return "I'll help you track the status of your requests. What specific information are you looking for?"
        
        # Default response with context consideration
        if context and len(context) > 0:
            return "I'm following our conversation. What specific aspect would you like me to help with or clarify?"
        
        return ("I'm ALEX, your general assistant. I can help with various tasks or connect you with our specialized agents. "
                "Feel free to ask anything, and I'll either help directly or involve the right specialist.")
