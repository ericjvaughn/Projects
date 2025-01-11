from typing import List, Dict, Optional
from app.agents.base_agent import BaseAgent, AgentResponse

class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "marketing"
        self.description = "Marketing strategy and campaign specialist"
        self.capabilities = [
            "marketing strategy",
            "campaign planning",
            "content marketing",
            "digital marketing",
            "social media",
            "email marketing",
            "marketing analytics",
            "audience targeting",
            "marketing automation"
        ]
        
        self.keywords = [
            "marketing", "campaign", "content", "digital",
            "social media", "email", "audience", "targeting",
            "analytics", "metrics", "ROI", "engagement",
            "automation", "leads", "funnel", "conversion",
            "advertising", "promotion", "channels"
        ]
        
        self.min_confidence_threshold = 0.35
    
    async def calculate_relevance(self, message: str) -> float:
        """Calculate relevance for marketing queries."""
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
        """Process marketing-related queries."""
        message = message.lower()
        confidence = await self.calculate_relevance(message)
        
        if await self._should_reroute(confidence):
            return AgentResponse(
                content="This query might be better handled by another specialist.",
                confidence=confidence,
                needs_rerouting=True
            )
        
        response_content = await self._generate_marketing_response(message, context)
        
        return AgentResponse(
            content=response_content,
            confidence=confidence,
            needs_rerouting=False
        )
    
    async def _generate_marketing_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Generate marketing-specific responses."""
        # Campaign and strategy queries
        if any(word in message for word in ["campaign", "strategy"]):
            return "I can help you develop effective marketing campaigns and strategies. Would you like to focus on digital, content, or traditional marketing approaches?"
        
        # Digital marketing queries
        if any(word in message for word in ["digital", "online", "internet"]):
            return "Let's discuss your digital marketing needs. I can help with SEO, PPC, social media, and other digital channels. What's your primary objective?"
        
        # Social media queries
        if "social" in message or "media" in message:
            return "I can assist with social media strategy, content planning, and engagement optimization. Which platforms are you most interested in?"
        
        # Analytics and metrics
        if any(word in message for word in ["analytics", "metrics", "roi", "performance"]):
            return "I'll help you track and analyze marketing performance. Would you like to focus on specific KPIs or get a general overview of your marketing metrics?"
        
        # Content marketing
        if "content" in message:
            return "Let's develop your content marketing strategy. I can help with content planning, creation guidelines, and distribution strategies. What type of content are you looking to create?"
        
        # Lead generation
        if any(word in message for word in ["leads", "funnel", "conversion"]):
            return "I can help optimize your marketing funnel for better lead generation and conversion. Where in the funnel would you like to focus?"
        
        # Default response
        return "I'm your marketing specialist. I can help with campaign planning, digital marketing, content strategy, analytics, and more. What aspect of marketing would you like to explore?"
