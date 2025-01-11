from app.agents.base_agent import BaseAgent

class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "sales_agent"
        self.description = "Specialized agent for handling sales-related queries"
        self.capabilities = [
            "product information",
            "pricing",
            "discounts",
            "promotions",
            "sales pipeline",
        ]
        
        # Keywords that indicate sales-related queries
        self.keywords = [
            "price", "cost", "discount", "deal", "purchase",
            "buy", "offer", "sale", "product", "package",
            "subscription", "payment", "quote"
        ]
    
    async def calculate_relevance(self, message: str) -> float:
        """
        Calculate relevance score based on presence of sales-related keywords.
        Returns a score between 0 and 1.
        """
        message = message.lower()
        keyword_matches = sum(1 for keyword in self.keywords if keyword in message)
        # Normalize score between 0 and 1
        return min(1.0, keyword_matches / 3)
    
    async def process_message(self, message: str) -> str:
        """Process sales-related queries and return appropriate responses."""
        message = message.lower()
        
        # Example logic for different types of sales queries
        if any(word in message for word in ["price", "cost"]):
            return "I can help you with pricing information. Could you specify which product you're interested in?"
        
        elif any(word in message for word in ["discount", "deal", "offer"]):
            return "We have several ongoing promotions. I can check what discounts are available for you."
        
        elif "product" in message:
            return "I'd be happy to provide detailed information about our products. What specific features are you looking for?"
        
        elif "purchase" in message or "buy" in message:
            return "Great! I can guide you through the purchase process. Would you like to know about our different packages?"
        
        else:
            return "I'm your sales assistant. I can help you with product information, pricing, discounts, and making a purchase. What would you like to know?"
