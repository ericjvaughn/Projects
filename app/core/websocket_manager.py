from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime
from pydantic import BaseModel

class WebSocketMessage(BaseModel):
    event: str
    data: dict
    room: Optional[str] = None

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_rooms: Dict[str, Set[str]] = {}
        self.room_clients: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new client."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # Send welcome message
        await self.send_personal_message(
            event="system",
            data={
                "message": "Connected to chat system",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            client_id=client_id
        )
    
    async def disconnect(self, client_id: str):
        """Disconnect a client and clean up their room memberships."""
        # Remove from all rooms
        if client_id in self.client_rooms:
            for room in self.client_rooms[client_id]:
                self.room_clients[room].remove(client_id)
                if not self.room_clients[room]:
                    del self.room_clients[room]
            del self.client_rooms[client_id]
        
        # Remove connection
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def join_room(self, client_id: str, room: str):
        """Add a client to a room."""
        # Initialize room if it doesn't exist
        if room not in self.room_clients:
            self.room_clients[room] = set()
        
        # Initialize client's room set if needed
        if client_id not in self.client_rooms:
            self.client_rooms[client_id] = set()
        
        # Add client to room
        self.room_clients[room].add(client_id)
        self.client_rooms[client_id].add(room)
        
        # Notify room members
        await self.broadcast_to_room(
            room=room,
            event="room_join",
            data={
                "client_id": client_id,
                "room": room,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def leave_room(self, client_id: str, room: str):
        """Remove a client from a room."""
        if room in self.room_clients and client_id in self.room_clients[room]:
            self.room_clients[room].remove(client_id)
            self.client_rooms[client_id].remove(room)
            
            # Clean up empty room
            if not self.room_clients[room]:
                del self.room_clients[room]
            
            # Notify remaining room members
            await self.broadcast_to_room(
                room=room,
                event="room_leave",
                data={
                    "client_id": client_id,
                    "room": room,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def send_personal_message(self, event: str, data: dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            message = WebSocketMessage(event=event, data=data)
            await self.active_connections[client_id].send_json(message.model_dump())
    
    async def broadcast(self, event: str, data: dict, exclude: Optional[str] = None):
        """Broadcast a message to all connected clients except excluded one."""
        message = WebSocketMessage(event=event, data=data)
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_json(message.model_dump())
    
    async def broadcast_to_room(self, room: str, event: str, data: dict, exclude: Optional[str] = None):
        """Broadcast a message to all clients in a room except excluded one."""
        if room not in self.room_clients:
            return
        
        message = WebSocketMessage(event=event, data=data, room=room)
        for client_id in self.room_clients[room]:
            if client_id != exclude and client_id in self.active_connections:
                await self.active_connections[client_id].send_json(message.model_dump())
    
    def get_room_members(self, room: str) -> Set[str]:
        """Get all client IDs in a room."""
        return self.room_clients.get(room, set())
    
    def get_client_rooms(self, client_id: str) -> Set[str]:
        """Get all rooms a client is in."""
        return self.client_rooms.get(client_id, set())
