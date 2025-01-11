from typing import Dict, Optional, List, Tuple
import asyncio
from fastapi import WebSocket
from pydantic import BaseModel
from app.core.shared_context import SharedContextManager, MessageContext

class Message(BaseModel):
    content: str
    sender_id: str
    mention: Optional[str] = None
    context_id: Optional[str] = None
    confidence_threshold: float = 0.3  # Minimum confidence for agent to handle message

class Response(BaseModel):
    content: str
    agent_name: str
    confidence: float
    needs_rerouting: bool = False

class Orchestrator:
    def __init__(self):
        self._agents: Dict[str, 'BaseAgent'] = {}
        self._active_connections: Dict[str, WebSocket] = {}
        self._context_manager = SharedContextManager()
        self._mention_pattern = r'@(\w+)'
    
    async def parse_mentions(self, message: str) -> List[str]:
        """Extract @mentions from message."""
        import re
        mentions = re.findall(self._mention_pattern, message)
        return [mention.lower() for mention in mentions]
    
    async def register_agent(self, agent: 'BaseAgent'):
        """Register a new agent with the orchestrator."""
        self._agents[agent.name] = agent
        print(f"Agent {agent.name} registered successfully")
    
    async def unregister_agent(self, agent_name: str):
        """Remove an agent from the orchestrator."""
        if agent_name in self._agents:
            del self._agents[agent_name]
            print(f"Agent {agent_name} unregistered successfully")
    
    async def route_message(self, message: Message) -> dict:
        """Route a message to appropriate agent(s) and aggregate responses."""
        # Create or update session context
        await self._context_manager.add_message(
            session_id=message.context_id,
            content=message.content,
            sender_id=message.sender_id
        )
        
        # Extract mentions
        mentions = await self.parse_mentions(message.content)
        responses = []
        
        if mentions:
            # Handle explicit mentions
            for mention in mentions:
                if mention in self._agents:
                    agent = self._agents[mention]
                    response = await self._process_agent_response(agent, message)
                    responses.append(response)
                    
                    # Update context with agent's response
                    await self._context_manager.add_message(
                        session_id=message.context_id,
                        content=response["content"],
                        sender_id=agent.name,
                        agent_id=agent.name,
                        confidence=response["confidence"]
                    )
                else:
                    responses.append({
                        "agent": "system",
                        "content": f"Agent @{mention} not found",
                        "confidence": 0.0
                    })
        else:
            # Find relevant agents based on content
            relevant_agents = await self._find_relevant_agents(
                message.content,
                threshold=message.confidence_threshold
            )
            
            if not relevant_agents:
                return {
                    "agent": "system",
                    "content": "No agent found suitable to handle this message",
                    "confidence": 0.0
                }
            
            # Process message with relevant agents
            for agent, confidence in relevant_agents:
                response = await self._process_agent_response(agent, message)
                if response["confidence"] >= message.confidence_threshold:
                    responses.append(response)
                    
                    # Update context with agent's response
                    await self._context_manager.add_message(
                        session_id=message.context_id,
                        content=response["content"],
                        sender_id=agent.name,
                        agent_id=agent.name,
                        confidence=response["confidence"]
                    )
        
        # Extend session TTL
        await self._context_manager.extend_session(message.context_id)
        
        # Aggregate responses
        return await self._aggregate_responses(responses)
    
    async def _find_relevant_agents(
        self,
        content: str,
        threshold: float = 0.3
    ) -> List[Tuple['BaseAgent', float]]:
        """Find agents relevant to the message content."""
        relevance_scores = []
        for agent in self._agents.values():
            confidence = await agent.calculate_relevance(content)
            if confidence >= threshold:
                relevance_scores.append((agent, confidence))
        
        # Sort by confidence
        return sorted(relevance_scores, key=lambda x: x[1], reverse=True)
    
    async def _process_agent_response(self, agent: 'BaseAgent', message: Message) -> dict:
        """Process message with an agent and handle potential rerouting."""
        # Get agent-specific context
        context = await self._context_manager.get_agent_context(
            message.context_id,
            agent.name
        )
        
        response = await agent.process_message(message.content, context)
        
        if response.needs_rerouting:
            # Try to find another agent if current one couldn't handle it
            other_agents = await self._find_relevant_agents(
                message.content,
                threshold=message.confidence_threshold
            )
            other_agents = [a for a, _ in other_agents if a.name != agent.name]
            
            if other_agents:
                new_response = await self._process_agent_response(
                    other_agents[0],
                    message
                )
                return new_response
        
        # Add agent to active agents list
        await self._context_manager.add_active_agent(
            message.context_id,
            agent.name
        )
        
        return {
            "agent": agent.name,
            "content": response.content,
            "confidence": response.confidence
        }
    
    async def _aggregate_responses(self, responses: List[dict]) -> dict:
        """Aggregate multiple agent responses."""
        if not responses:
            return {
                "agent": "system",
                "content": "No agents were able to process your message",
                "confidence": 0.0
            }
        
        # If only one response, return it directly
        if len(responses) == 1:
            return responses[0]
        
        # Combine multiple responses
        agents = [r["agent"] for r in responses]
        contents = [r["content"] for r in responses]
        max_confidence = max(r["confidence"] for r in responses)
        
        return {
            "agent": f"multiple({', '.join(agents)})",
            "content": "\n\n".join([
                f"[{agent}]: {content}"
                for agent, content in zip(agents, contents)
            ]),
            "confidence": max_confidence
        }
    
    async def register_connection(self, websocket: WebSocket, client_id: str):
        """Register a new WebSocket connection."""
        await websocket.accept()
        self._active_connections[client_id] = websocket
    
    async def unregister_connection(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self._active_connections:
            del self._active_connections[client_id]
    
    async def broadcast_message(self, message: dict, exclude_client: Optional[str] = None):
        """Broadcast a message to all connected clients except the sender."""
        for client_id, connection in self._active_connections.items():
            if client_id != exclude_client:
                await connection.send_json(message)

# Global orchestrator instance
orchestrator = Orchestrator()
