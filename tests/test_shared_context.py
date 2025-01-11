import pytest
from datetime import datetime, timedelta
import json
from app.core.shared_context import MessageContext, SessionContext

@pytest.mark.asyncio
async def test_create_session(shared_context):
    """Test session creation."""
    session_id = "test_session"
    session = await shared_context.create_session(session_id)
    
    assert session.session_id == session_id
    assert session.messages == []
    assert session.active_agents == set()
    assert session.metadata == {}

@pytest.mark.asyncio
async def test_add_message(shared_context):
    """Test adding messages to a session."""
    session_id = "test_session"
    message = MessageContext(
        content="Test message",
        sender="user",
        timestamp=datetime.utcnow(),
        metadata={"key": "value"}
    )
    
    await shared_context.add_message(session_id, message)
    session = await shared_context.get_session(session_id)
    
    assert len(session.messages) == 1
    assert session.messages[0].content == message.content
    assert session.messages[0].sender == message.sender
    assert session.messages[0].metadata == message.metadata

@pytest.mark.asyncio
async def test_get_recent_messages(shared_context):
    """Test retrieving recent messages from a session."""
    session_id = "test_session"
    messages = [
        MessageContext(
            content=f"Message {i}",
            sender="user",
            timestamp=datetime.utcnow() - timedelta(minutes=i)
        )
        for i in range(5)
    ]
    
    for msg in messages:
        await shared_context.add_message(session_id, msg)
    
    # Get last 3 messages
    recent = await shared_context.get_recent_messages(session_id, limit=3)
    assert len(recent) == 3
    assert recent[0].content == "Message 2"
    assert recent[-1].content == "Message 0"

@pytest.mark.asyncio
async def test_update_active_agents(shared_context):
    """Test updating active agents in a session."""
    session_id = "test_session"
    agents = {"sales", "marketing"}
    
    await shared_context.update_active_agents(session_id, agents)
    session = await shared_context.get_session(session_id)
    
    assert session.active_agents == agents

@pytest.mark.asyncio
async def test_update_metadata(shared_context):
    """Test updating session metadata."""
    session_id = "test_session"
    metadata = {"key1": "value1", "key2": "value2"}
    
    await shared_context.update_metadata(session_id, metadata)
    session = await shared_context.get_session(session_id)
    
    assert session.metadata == metadata

@pytest.mark.asyncio
async def test_session_expiration(shared_context, redis_mock):
    """Test that sessions expire after TTL."""
    session_id = "test_session"
    await shared_context.create_session(session_id)
    
    # Simulate TTL expiration
    await redis_mock.delete(f"session:{session_id}")
    
    session = await shared_context.get_session(session_id)
    assert session is None

@pytest.mark.asyncio
async def test_message_order(shared_context):
    """Test that messages maintain chronological order."""
    session_id = "test_session"
    now = datetime.utcnow()
    
    messages = [
        MessageContext(
            content=f"Message {i}",
            sender="user",
            timestamp=now + timedelta(minutes=i)
        )
        for i in range(3)
    ]
    
    # Add messages in reverse order
    for msg in reversed(messages):
        await shared_context.add_message(session_id, msg)
    
    session = await shared_context.get_session(session_id)
    assert len(session.messages) == 3
    assert session.messages[0].content == "Message 0"
    assert session.messages[-1].content == "Message 2"

@pytest.mark.asyncio
async def test_invalid_session(shared_context):
    """Test handling of invalid session IDs."""
    session = await shared_context.get_session("nonexistent_session")
    assert session is None
    
    # Test operations on invalid session
    message = MessageContext(
        content="Test message",
        sender="user",
        timestamp=datetime.utcnow()
    )
    
    with pytest.raises(ValueError):
        await shared_context.add_message("nonexistent_session", message)

@pytest.mark.asyncio
async def test_concurrent_updates(shared_context):
    """Test concurrent updates to the same session."""
    session_id = "test_session"
    await shared_context.create_session(session_id)
    
    # Simulate concurrent message additions
    messages = [
        MessageContext(
            content=f"Concurrent message {i}",
            sender="user",
            timestamp=datetime.utcnow()
        )
        for i in range(5)
    ]
    
    await asyncio.gather(
        *[shared_context.add_message(session_id, msg) for msg in messages]
    )
    
    session = await shared_context.get_session(session_id)
    assert len(session.messages) == 5

@pytest.mark.asyncio
async def test_message_validation(shared_context):
    """Test validation of message content."""
    session_id = "test_session"
    
    # Test empty content
    with pytest.raises(ValueError):
        await shared_context.add_message(
            session_id,
            MessageContext(
                content="",
                sender="user",
                timestamp=datetime.utcnow()
            )
        )
    
    # Test invalid timestamp
    with pytest.raises(ValueError):
        await shared_context.add_message(
            session_id,
            MessageContext(
                content="Test message",
                sender="user",
                timestamp=datetime.utcnow() + timedelta(days=1)  # Future timestamp
            )
        )
