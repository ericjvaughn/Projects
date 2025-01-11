from typing import Dict, List, Optional
import json
from datetime import datetime
import redis.asyncio as redis

class ContextManager:
    def __init__(self):
        self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        self.context_ttl = 3600  # 1 hour in seconds
    
    async def get_context(self, context_id: str) -> List[Dict]:
        """Retrieve conversation context for a given context_id."""
        if not context_id:
            return []
        
        context_data = await self.redis_client.get(f"context:{context_id}")
        if not context_data:
            return []
        
        return json.loads(context_data)
    
    async def update_context(self, context_id: str, message: str):
        """Update conversation context with a new message."""
        if not context_id:
            return
        
        context_data = await self.get_context(context_id)
        
        # Add new message to context
        context_data.append({
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Keep only last 10 messages for context
        if len(context_data) > 10:
            context_data = context_data[-10:]
        
        # Store updated context
        await self.redis_client.set(
            f"context:{context_id}",
            json.dumps(context_data),
            ex=self.context_ttl
        )
    
    async def clear_context(self, context_id: str):
        """Clear conversation context for a given context_id."""
        await self.redis_client.delete(f"context:{context_id}")
    
    async def extend_context_ttl(self, context_id: str):
        """Extend the TTL for a context."""
        await self.redis_client.expire(f"context:{context_id}", self.context_ttl)
