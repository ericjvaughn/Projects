import pytest
import asyncio
from typing import Dict, List
import fakeredis.aioredis
from unittest.mock import AsyncMock, patch

from app.core.shared_context import SharedContextManager
from app.orchestrator import Orchestrator, Message
from app.agents.base_agent import BaseAgent, AgentResponse

class MockAgent(BaseAgent):
    def __init__(self, name: str, confidence: float = 0.8):
        super().__init__()
        self.name = name
        self.default_confidence = confidence
        self.process_message_mock = AsyncMock()
        self.calculate_relevance_mock = AsyncMock(return_value=confidence)
    
    async def process_message(self, message: str, context: List[Dict] = None) -> AgentResponse:
        return await self.process_message_mock(message, context)
    
    async def calculate_relevance(self, message: str) -> float:
        return await self.calculate_relevance_mock(message)

@pytest.fixture
async def redis_mock():
    """Create a mock Redis instance using fakeredis."""
    redis = await fakeredis.aioredis.create_redis_pool()
    yield redis
    redis.close()
    await redis.wait_closed()

@pytest.fixture
async def shared_context(redis_mock):
    """Create a SharedContextManager instance with mock Redis."""
    with patch('app.core.shared_context.redis.from_url', return_value=redis_mock):
        context_manager = SharedContextManager()
        yield context_manager

@pytest.fixture
def mock_sales_agent():
    """Create a mock sales agent."""
    agent = MockAgent("sales")
    agent.process_message_mock.return_value = AgentResponse(
        content="I can help with sales inquiries",
        confidence=0.8,
        needs_rerouting=False
    )
    return agent

@pytest.fixture
def mock_marketing_agent():
    """Create a mock marketing agent."""
    agent = MockAgent("marketing")
    agent.process_message_mock.return_value = AgentResponse(
        content="I can help with marketing strategies",
        confidence=0.8,
        needs_rerouting=False
    )
    return agent

@pytest.fixture
def mock_low_confidence_agent():
    """Create a mock agent that always has low confidence."""
    agent = MockAgent("low_confidence", confidence=0.2)
    agent.process_message_mock.return_value = AgentResponse(
        content="I'm not confident about this",
        confidence=0.2,
        needs_rerouting=True
    )
    return agent

@pytest.fixture
async def orchestrator(shared_context, mock_sales_agent, mock_marketing_agent):
    """Create an Orchestrator instance with mock agents."""
    orchestrator = Orchestrator()
    await orchestrator.register_agent(mock_sales_agent)
    await orchestrator.register_agent(mock_marketing_agent)
    return orchestrator

@pytest.fixture
def message_factory():
    """Factory function to create test messages."""
    def create_message(
        content: str,
        sender_id: str = "test_user",
        mention: str = None,
        context_id: str = "test_context",
        confidence_threshold: float = 0.3
    ) -> Message:
        return Message(
            content=content,
            sender_id=sender_id,
            mention=mention,
            context_id=context_id,
            confidence_threshold=confidence_threshold
        )
    return create_message

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
