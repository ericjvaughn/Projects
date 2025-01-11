from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import json

from app.core.config import settings
from app.core.agent_manager import AgentManager
from app.core.session_manager import SessionManager
from app.core.message_router import MessageRouter

app = FastAPI(title="Multi-Agent Chat System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
agent_manager = AgentManager()
session_manager = SessionManager()
message_router = MessageRouter(agent_manager)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    async def broadcast(self, message: str, exclude: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_text(message)

ws_manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message through the router
            response = await message_router.route_message(
                message_data["content"],
                message_data.get("mention"),
                client_id
            )
            
            # Update session context
            await session_manager.update_context(client_id, message_data["content"])
            
            # Send response back to the client
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
        await ws_manager.broadcast(f"Client #{client_id} left the chat")

@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup."""
    # Initialize agents
    agent_manager.startup()
    
    print(f"Multi-agent chat system initialized and ready for WebSocket connections on port {settings.PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    # Clean up WebSocket connections
    for client_id in list(ws_manager.active_connections.keys()):
        await ws_manager.disconnect(client_id)
    
    print("Multi-agent chat system shut down successfully")
