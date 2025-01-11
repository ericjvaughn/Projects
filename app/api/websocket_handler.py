from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
import json
import uuid
from datetime import datetime

from app.core.websocket_manager import WebSocketManager
from app.orchestrator import orchestrator, Message

router = APIRouter()
ws_manager = WebSocketManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle WebSocket connections and messages."""
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process message based on event type
            await handle_websocket_message(client_id, data)
            
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)
        
        # Notify other clients
        await ws_manager.broadcast(
            event="client_disconnect",
            data={
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude=client_id
        )

async def handle_websocket_message(client_id: str, data: dict):
    """Handle different types of WebSocket messages."""
    event = data.get("event")
    message_data = data.get("data", {})
    
    if event == "chat_message":
        await handle_chat_message(client_id, message_data)
    
    elif event == "join_room":
        room = message_data.get("room")
        if room:
            await ws_manager.join_room(client_id, room)
    
    elif event == "leave_room":
        room = message_data.get("room")
        if room:
            await ws_manager.leave_room(client_id, room)
    
    elif event == "typing_status":
        await handle_typing_status(client_id, message_data)

async def handle_chat_message(client_id: str, message_data: dict):
    """Process chat messages and route through orchestrator."""
    content = message_data.get("content")
    if not content:
        return
    
    # Generate or use provided session ID
    session_id = message_data.get("session_id", str(uuid.uuid4()))
    
    # Create message for orchestrator
    message = Message(
        content=content,
        sender_id=client_id,
        mention=message_data.get("mention"),
        context_id=session_id,
        confidence_threshold=message_data.get("confidence_threshold", 0.3)
    )
    
    # Route message through orchestrator
    response = await orchestrator.route_message(message)
    
    # Broadcast response to appropriate room/client
    if message_data.get("room"):
        await ws_manager.broadcast_to_room(
            room=message_data["room"],
            event="chat_response",
            data={
                "response": response,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    else:
        await ws_manager.send_personal_message(
            event="chat_response",
            data={
                "response": response,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id=client_id
        )

async def handle_typing_status(client_id: str, data: dict):
    """Handle typing status updates."""
    room = data.get("room")
    is_typing = data.get("is_typing", False)
    
    # Broadcast typing status
    if room:
        await ws_manager.broadcast_to_room(
            room=room,
            event="typing_status",
            data={
                "client_id": client_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude=client_id
        )
