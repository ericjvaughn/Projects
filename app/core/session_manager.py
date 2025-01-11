import json
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from app.core.config import settings

class SessionManager:
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.mongo_client[settings.DATABASE_NAME]
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
    async def get_context(self, session_id: str) -> Dict:
        """Retrieve session context from Redis (recent) and MongoDB (historical)."""
        # Get recent context from Redis
        recent_context = await self.redis_client.get(f"context:{session_id}")
        recent_context = json.loads(recent_context) if recent_context else []
        
        # Get historical context from MongoDB
        historical_context = await self.db.contexts.find_one({"session_id": session_id})
        historical_context = historical_context["context"] if historical_context else []
        
        return {
            "recent": recent_context,
            "historical": historical_context
        }
    
    async def update_context(self, session_id: str, message: str):
        """Update session context in both Redis and MongoDB."""
        # Update recent context in Redis
        recent_context = await self.redis_client.get(f"context:{session_id}")
        recent_context = json.loads(recent_context) if recent_context else []
        recent_context.append(message)
        
        # Keep only last 10 messages in recent context
        if len(recent_context) > 10:
            recent_context = recent_context[-10:]
        
        await self.redis_client.set(
            f"context:{session_id}",
            json.dumps(recent_context),
            ex=3600  # Expire after 1 hour
        )
        
        # Update historical context in MongoDB
        await self.db.contexts.update_one(
            {"session_id": session_id},
            {
                "$push": {
                    "context": {
                        "$each": [message],
                        "$slice": -100  # Keep last 100 messages
                    }
                }
            },
            upsert=True
        )
    
    async def clear_context(self, session_id: str):
        """Clear session context from both Redis and MongoDB."""
        await self.redis_client.delete(f"context:{session_id}")
        await self.db.contexts.delete_one({"session_id": session_id})
