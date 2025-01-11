import pytest
from unittest.mock import AsyncMock
from app.orchestrator import Message

@pytest.mark.asyncio
async def test_orchestrator_mention_routing(orchestrator, message_factory):
    """Test that messages with mentions are routed to the correct agent."""
    message = message_factory("Help with sales", mention="sales")
    response = await orchestrator.route_message(message)
    
    assert response["agent"] == "sales"
    assert "help with sales" in response["content"].lower()
    assert response["confidence"] >= 0.3

@pytest.mark.asyncio
async def test_orchestrator_content_based_routing(orchestrator, message_factory):
    """Test that messages are routed based on content relevance."""
    message = message_factory("What's our marketing strategy?")
    response = await orchestrator.route_message(message)
    
    assert response["agent"] == "marketing"
    assert "marketing" in response["content"].lower()
    assert response["confidence"] >= 0.3

@pytest.mark.asyncio
async def test_orchestrator_no_suitable_agent(
    orchestrator,
    message_factory,
    mock_low_confidence_agent
):
    """Test handling when no agent is confident enough to handle the message."""
    # Register a low confidence agent
    await orchestrator.register_agent(mock_low_confidence_agent)
    
    # Create a message that no agent is confident about
    message = message_factory(
        "Something completely unrelated",
        confidence_threshold=0.5
    )
    response = await orchestrator.route_message(message)
    
    assert response["agent"] == "system"
    assert "no agent" in response["content"].lower()
    assert response["confidence"] == 0.0

@pytest.mark.asyncio
async def test_orchestrator_multiple_mentions(orchestrator, message_factory):
    """Test handling messages with multiple agent mentions."""
    message = message_factory(
        "@sales what's our pricing and @marketing how's our campaign?",
    )
    response = await orchestrator.route_message(message)
    
    assert "multiple" in response["agent"]
    assert "sales" in response["agent"]
    assert "marketing" in response["agent"]
    assert response["confidence"] >= 0.3

@pytest.mark.asyncio
async def test_orchestrator_agent_rerouting(
    orchestrator,
    message_factory,
    mock_low_confidence_agent
):
    """Test that messages are rerouted when an agent can't handle them."""
    await orchestrator.register_agent(mock_low_confidence_agent)
    
    # Message mentioning the low confidence agent
    message = message_factory("Help me", mention="low_confidence")
    response = await orchestrator.route_message(message)
    
    # Should be rerouted to another agent
    assert response["agent"] != "low_confidence"
    assert response["confidence"] >= 0.3

@pytest.mark.asyncio
async def test_orchestrator_invalid_mention(orchestrator, message_factory):
    """Test handling of mentions to non-existent agents."""
    message = message_factory("Help me", mention="nonexistent_agent")
    response = await orchestrator.route_message(message)
    
    assert response["agent"] == "system"
    assert "not found" in response["content"].lower()
    assert response["confidence"] == 0.0

@pytest.mark.asyncio
async def test_orchestrator_empty_message(orchestrator, message_factory):
    """Test handling of empty messages."""
    message = message_factory("   ")
    response = await orchestrator.route_message(message)
    
    assert response["agent"] == "system"
    assert "empty" in response["content"].lower()
    assert response["confidence"] == 0.0

@pytest.mark.asyncio
async def test_orchestrator_agent_registration(orchestrator, mock_low_confidence_agent):
    """Test agent registration and unregistration."""
    # Test registration
    await orchestrator.register_agent(mock_low_confidence_agent)
    assert mock_low_confidence_agent.name in orchestrator._agents
    
    # Test unregistration
    await orchestrator.unregister_agent(mock_low_confidence_agent.name)
    assert mock_low_confidence_agent.name not in orchestrator._agents

@pytest.mark.asyncio
async def test_orchestrator_context_handling(orchestrator, message_factory, shared_context):
    """Test that context is properly maintained across messages."""
    # Send first message
    message1 = message_factory("First message")
    await orchestrator.route_message(message1)
    
    # Send second message
    message2 = message_factory("Second message", context_id=message1.context_id)
    response = await orchestrator.route_message(message2)
    
    # Verify context was maintained
    context = await shared_context.get_session(message1.context_id)
    assert context is not None
    assert len(context.messages) >= 2
