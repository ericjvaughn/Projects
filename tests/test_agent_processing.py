import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.agents.base_agent import AgentResponse
from app.core.shared_context import MessageContext

@pytest.mark.asyncio
async def test_agent_response_validation(mock_sales_agent):
    """Test validation of agent responses."""
    # Test valid response
    mock_sales_agent.process_message_mock.return_value = AgentResponse(
        content="Valid response",
        confidence=0.8,
        needs_rerouting=False
    )
    response = await mock_sales_agent.process_message("Test message")
    assert response.content == "Valid response"
    assert response.confidence == 0.8
    
    # Test invalid confidence
    mock_sales_agent.process_message_mock.return_value = AgentResponse(
        content="Invalid confidence",
        confidence=1.5,  # Invalid confidence > 1
        needs_rerouting=False
    )
    with pytest.raises(ValueError):
        await mock_sales_agent.process_message("Test message")

@pytest.mark.asyncio
async def test_agent_context_processing(mock_sales_agent, shared_context):
    """Test agent processing with context."""
    session_id = "test_session"
    context_messages = [
        MessageContext(
            content="Previous message 1",
            sender="user",
            timestamp=datetime.utcnow()
        ),
        MessageContext(
            content="Previous message 2",
            sender="sales",
            timestamp=datetime.utcnow()
        )
    ]
    
    # Add context messages
    for msg in context_messages:
        await shared_context.add_message(session_id, msg)
    
    # Process message with context
    context = await shared_context.get_recent_messages(session_id)
    await mock_sales_agent.process_message("New message", context)
    
    # Verify context was passed to process_message
    mock_sales_agent.process_message_mock.assert_called_with(
        "New message",
        context
    )

@pytest.mark.asyncio
async def test_agent_confidence_calculation(mock_sales_agent):
    """Test agent confidence calculation."""
    # Test high confidence case
    mock_sales_agent.calculate_relevance_mock.return_value = 0.9
    confidence = await mock_sales_agent.calculate_relevance("Sales related query")
    assert confidence == 0.9
    
    # Test low confidence case
    mock_sales_agent.calculate_relevance_mock.return_value = 0.2
    confidence = await mock_sales_agent.calculate_relevance("Unrelated query")
    assert confidence == 0.2

@pytest.mark.asyncio
async def test_agent_rerouting(mock_sales_agent):
    """Test agent rerouting logic."""
    # Test successful processing
    mock_sales_agent.process_message_mock.return_value = AgentResponse(
        content="I can handle this",
        confidence=0.8,
        needs_rerouting=False
    )
    response = await mock_sales_agent.process_message("Sales question")
    assert not response.needs_rerouting
    
    # Test rerouting needed
    mock_sales_agent.process_message_mock.return_value = AgentResponse(
        content="Need help from marketing",
        confidence=0.3,
        needs_rerouting=True
    )
    response = await mock_sales_agent.process_message("Marketing question")
    assert response.needs_rerouting

@pytest.mark.asyncio
async def test_agent_error_handling(mock_sales_agent):
    """Test agent error handling."""
    # Simulate processing error
    mock_sales_agent.process_message_mock.side_effect = Exception("Processing error")
    
    response = await mock_sales_agent.process_message("Test message")
    assert response.needs_rerouting
    assert response.confidence == 0.0
    assert "error" in response.content.lower()

@pytest.mark.asyncio
async def test_agent_metadata_handling(mock_sales_agent, shared_context):
    """Test agent handling of metadata."""
    session_id = "test_session"
    metadata = {"customer_id": "12345", "priority": "high"}
    
    # Add message with metadata
    await shared_context.create_session(session_id)
    await shared_context.update_metadata(session_id, metadata)
    
    # Process message
    context = await shared_context.get_session(session_id)
    await mock_sales_agent.process_message("Test message", context.messages)
    
    # Verify metadata was passed
    mock_sales_agent.process_message_mock.assert_called_with(
        "Test message",
        context.messages
    )

@pytest.mark.asyncio
async def test_agent_response_formatting(mock_sales_agent):
    """Test agent response formatting."""
    # Test HTML content
    mock_sales_agent.process_message_mock.return_value = AgentResponse(
        content="<script>alert('test')</script>Response",
        confidence=0.8,
        needs_rerouting=False
    )
    response = await mock_sales_agent.process_message("Test message")
    assert "<script>" not in response.content
    
    # Test long response
    long_content = "x" * 10000
    mock_sales_agent.process_message_mock.return_value = AgentResponse(
        content=long_content,
        confidence=0.8,
        needs_rerouting=False
    )
    response = await mock_sales_agent.process_message("Test message")
    assert len(response.content) <= 2000  # Assuming max length is 2000

@pytest.mark.asyncio
async def test_agent_concurrent_processing(mock_sales_agent):
    """Test concurrent message processing."""
    messages = [f"Message {i}" for i in range(5)]
    
    # Process messages concurrently
    responses = await asyncio.gather(
        *[mock_sales_agent.process_message(msg) for msg in messages]
    )
    
    assert len(responses) == 5
    assert all(isinstance(r, AgentResponse) for r in responses)

@pytest.mark.asyncio
async def test_agent_rate_limiting(mock_sales_agent):
    """Test agent rate limiting."""
    # Simulate rapid message processing
    for _ in range(10):
        await mock_sales_agent.process_message("Test message")
    
    # Verify rate limiting
    mock_sales_agent.process_message_mock.assert_called()
    assert mock_sales_agent.process_message_mock.call_count <= 10
