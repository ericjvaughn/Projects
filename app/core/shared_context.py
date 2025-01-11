from typing import Dict, List, Optional, Set
import json
from datetime import datetime, timedelta
import redis.asyncio as redis
from pydantic import BaseModel

class MessageContext(BaseModel):
    content: str
    timestamp: str
    sender_id: str
    agent_id: Optional[str] = None
    confidence: Optional[float] = None

class SessionContext(BaseModel):
    session_id: str
    created_at: str
    last_updated: str
    active_agents: Set[str]
    messages: List[MessageContext]
    metadata: Dict = {}

class SharedContextManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.session_ttl = 3600  # 1 hour
        self.context_prefix = "context:"
        self.session_prefix = "session:"
        self.agent_prefix = "agent:"
    
    async def create_session(self, session_id: str) -> SessionContext:
        """Create a new session context."""
        now = datetime.utcnow().isoformat()
        session = SessionContext(
            session_id=session_id,
            created_at=now,
            last_updated=now,
            active_agents=set(),
            messages=[],
            metadata={}
        )
        
        await self._save_session(session)
        return session
    
    async def add_message(
        self,
        session_id: str,
        content: str,
        sender_id: str,
        agent_id: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """Add a message to the session context."""
        session = await self.get_session(session_id)
        if not session:
            session = await self.create_session(session_id)
        
        message = MessageContext(
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            sender_id=sender_id,
            agent_id=agent_id,
            confidence=confidence
        )
        
        session.messages.append(message)
        session.last_updated = datetime.utcnow().isoformat()
        
        if agent_id:
            session.active_agents.add(agent_id)
        
        await self._save_session(session)
        return True
    
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Retrieve a session context."""
        session_data = await self.redis.get(f"{self.session_prefix}{session_id}")
        if not session_data:
            return None
        
        session_dict = json.loads(session_data)
        return SessionContext(**session_dict)
    
    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[MessageContext]:
        """Get recent messages from a session."""
        session = await self.get_session(session_id)
        if not session:
            return []
        
        return session.messages[-limit:]
    
    async def get_agent_context(
        self,
        session_id: str,
        agent_id: str
    ) -> List[MessageContext]:
        """Get context specific to an agent."""
        session = await self.get_session(session_id)
        if not session:
            return []
        
        # Filter messages relevant to the agent
        return [
            msg for msg in session.messages
            if msg.agent_id == agent_id or not msg.agent_id
        ]
    
    async def update_metadata(
        self,
        session_id: str,
        metadata: Dict
    ) -> bool:
        """Update session metadata."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.metadata.update(metadata)
        session.last_updated = datetime.utcnow().isoformat()
        
        await self._save_session(session)
        return True
    
    async def add_active_agent(
        self,
        session_id: str,
        agent_id: str
    ) -> bool:
        """Add an agent to the active agents list."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.active_agents.add(agent_id)
        session.last_updated = datetime.utcnow().isoformat()
        
        await self._save_session(session)
        return True
    
    async def get_active_agents(self, session_id: str) -> Set[str]:
        """Get list of active agents in the session."""
        session = await self.get_session(session_id)
        if not session:
            return set()
        
        return session.active_agents
    
    async def _save_session(self, session: SessionContext):
        """Save session data to Redis."""
        session_data = session.model_dump_json()
        await self.redis.set(
            f"{self.session_prefix}{session.session_id}",
            session_data,
            ex=self.session_ttl
        )
    
    async def extend_session(self, session_id: str):
        """Extend the TTL of a session."""
        await self.redis.expire(
            f"{self.session_prefix}{session_id}",
            self.session_ttl
        )
