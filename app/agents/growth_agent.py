from typing import List, Dict, Optional
from app.agents.base_agent import BaseAgent, AgentResponse

class GrowthAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "growth"
        self.description = "Growth strategy and optimization specialist"
        self.capabilities = [
            "growth strategy",
            "market expansion",
            "user acquisition",
            "retention optimization",
            "growth modeling",
            "scalability planning",
            "product-market fit",
            "growth experiments",
            "monetization strategy"
        ]
        
        self.keywords = [
            "growth", "scale", "expansion", "acquisition",
            "retention", "churn", "monetization", "revenue",
            "optimization", "experiments", "metrics", "kpi",
            "product-market", "user base", "market share",
            "scalability", "growth hack", "viral", "expansion"
        ]
        
        self.min_confidence_threshold = 0.35
    
    async def calculate_relevance(self, message: str) -> float:
        """Calculate relevance for growth-related queries."""
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
        """Process growth-related queries."""
        message = message.lower()
        confidence = await self.calculate_relevance(message)
        
        if await self._should_reroute(confidence):
            return AgentResponse(
                content="This query might be better handled by another specialist.",
                confidence=confidence,
                needs_rerouting=True
            )
        
        response_content = await self._generate_growth_response(message, context)
        
        return AgentResponse(
            content=response_content,
            confidence=confidence,
            needs_rerouting=False
        )
    
    async def _generate_growth_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Generate growth-specific responses."""
        # Growth strategy queries
        if any(word in message for word in ["strategy", "plan"]):
            return "I can help develop comprehensive growth strategies. Would you like to focus on user acquisition, retention, or monetization strategies?"
        
        # Market expansion
        if any(word in message for word in ["expansion", "market", "scale"]):
            return "Let's discuss market expansion opportunities. I can help analyze new markets, entry strategies, and scaling approaches. What's your primary expansion goal?"
        
        # User acquisition
        if any(word in message for word in ["acquisition", "users", "customers"]):
            return "I'll help optimize your user acquisition strategy. We can explore different channels, optimize CAC, and improve conversion rates. What's your current acquisition focus?"
        
        # Retention optimization
        if any(word in message for word in ["retention", "churn"]):
            return "Let's work on improving user retention. I can help analyze churn patterns, develop retention strategies, and optimize the user lifecycle. Where would you like to start?"
        
        # Growth experiments
        if any(word in message for word in ["experiment", "test", "optimize"]):
            return "I can help design and analyze growth experiments. Would you like to focus on A/B testing, funnel optimization, or feature experimentation?"
        
        # Monetization
        if any(word in message for word in ["monetization", "revenue"]):
            return "Let's optimize your monetization strategy. We can explore pricing models, revenue optimization, and value proposition enhancement. What's your current monetization challenge?"
        
        # Default response
        return "I'm your growth specialist. I can help with user acquisition, retention optimization, market expansion, and monetization strategies. What growth challenge would you like to tackle?"
