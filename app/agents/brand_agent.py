from typing import List, Dict, Optional
from app.agents.base_agent import BaseAgent, AgentResponse

class BrandAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "brand"
        self.description = "Brand strategy and management specialist"
        self.capabilities = [
            "brand strategy",
            "brand identity",
            "brand positioning",
            "brand voice",
            "visual identity",
            "brand guidelines",
            "brand messaging",
            "brand experience",
            "brand reputation",
            "brand consistency"
        ]
        
        self.keywords = [
            "brand", "identity", "positioning", "voice",
            "visual", "logo", "design", "guidelines",
            "messaging", "reputation", "values", "personality",
            "perception", "experience", "consistency", "story",
            "narrative", "image", "awareness"
        ]
        
        self.min_confidence_threshold = 0.35
    
    async def calculate_relevance(self, message: str) -> float:
        """Calculate relevance for brand-related queries."""
        message = message.lower()
        
        # Check keyword matches
        keyword_matches = sum(1 for keyword in self.keywords if keyword in message)
        keyword_score = min(1.0, keyword_matches / 2)
        
        # Check capability matches
        capability_score = await self._check_capability_match(message)
        
        # Combine scores with weights
        final_score = (keyword_score * 0.6) + (capability_score * 0.4)
        return final_score
    
    async def process_message(self, message: str, context: Optional[List[Dict]] = None) -> AgentResponse:
        """Process brand-related queries."""
        message = message.lower()
        confidence = await self.calculate_relevance(message)
        
        if await self._should_reroute(confidence):
            return AgentResponse(
                content="This query might be better handled by another specialist.",
                confidence=confidence,
                needs_rerouting=True
            )
        
        response_content = await self._generate_brand_response(message, context)
        
        return AgentResponse(
            content=response_content,
            confidence=confidence,
            needs_rerouting=False
        )
    
    async def _generate_brand_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Generate brand-specific responses."""
        # Brand strategy queries
        if any(word in message for word in ["strategy", "positioning"]):
            return "I can help develop your brand strategy and positioning. Would you like to focus on market positioning, brand differentiation, or value proposition?"
        
        # Brand identity
        if any(word in message for word in ["identity", "visual", "logo", "design"]):
            return "Let's work on your brand identity. I can help with visual elements, design principles, and brand guidelines. What aspect of your brand identity needs attention?"
        
        # Brand voice and messaging
        if any(word in message for word in ["voice", "messaging", "communication"]):
            return "I'll help define and refine your brand voice and messaging strategy. Would you like to focus on tone of voice, key messages, or communication guidelines?"
        
        # Brand experience
        if "experience" in message:
            return "Let's enhance your brand experience. We can work on customer touchpoints, brand interactions, and experience consistency. Where would you like to start?"
        
        # Brand reputation
        if any(word in message for word in ["reputation", "perception"]):
            return "I can help manage and enhance your brand reputation. Would you like to focus on reputation monitoring, management strategies, or improvement initiatives?"
        
        # Brand guidelines
        if "guidelines" in message:
            return "I'll help develop comprehensive brand guidelines. This can include visual standards, voice guidelines, and usage rules. What specific aspects need documentation?"
        
        # Brand awareness
        if any(word in message for word in ["awareness", "recognition"]):
            return "Let's work on building brand awareness. We can develop strategies for increasing visibility and recognition in your target market. What are your awareness goals?"
        
        # Default response
        return "I'm your brand specialist. I can help with brand strategy, identity, positioning, voice, and reputation management. What aspect of your brand would you like to develop?"
