from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Optional
from pydantic import BaseModel
import uuid

from app.orchestrator import orchestrator, Message
from app.agents.alex_agent import AlexAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.sales_agent import SalesAgent
from app.agents.growth_agent import GrowthAgent
from app.agents.brand_agent import BrandAgent
from app.agents.strategic_agent import StrategicAgent

router = APIRouter()

class MessageRequest(BaseModel):
    content: str
    sender_id: str
    mention: Optional[str] = None
    context_id: Optional[str] = None

@router.post("/message")
async def handle_message(request: MessageRequest):
    """Handle incoming messages via REST API."""
    message = Message(
        content=request.content,
        sender_id=request.sender_id,
        mention=request.mention,
        context_id=request.context_id or str(uuid.uuid4())
    )
    
    try:
        response = await orchestrator.route_message(message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle WebSocket connections for real-time chat."""
    await orchestrator.register_connection(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            message = Message(
                content=data["content"],
                sender_id=client_id,
                mention=data.get("mention"),
                context_id=data.get("context_id", str(uuid.uuid4()))
            )
            
            response = await orchestrator.route_message(message)
            await websocket.send_json(response)
            
            # Broadcast message to other clients if needed
            if data.get("broadcast", False):
                await orchestrator.broadcast_message(response, exclude_client=client_id)
                
    except WebSocketDisconnect:
        await orchestrator.unregister_connection(client_id)
    except Exception as e:
        await websocket.close(code=1001, reason=str(e))

@router.on_event("startup")
async def startup_event():
    """Initialize and register agents when the application starts."""
    # Register all agents
    await orchestrator.register_agent(AlexAgent())
    await orchestrator.register_agent(MarketingAgent())
    await orchestrator.register_agent(SalesAgent())
    await orchestrator.register_agent(GrowthAgent())
    await orchestrator.register_agent(BrandAgent())
    
    print("Multi-agent chat system initialized with all agents successfully")
