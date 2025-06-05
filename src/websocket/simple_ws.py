"""Simple WebSocket endpoint using FastAPI's built-in WebSocket support."""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import json
import asyncio
from loguru import logger


class SimpleConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """Accept and track a new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
        
        # Send initial message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Connected to CX Futurist AI WebSocket"
        })
        
    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


# Global connection manager
ws_manager = SimpleConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
                elif message.get("type") == "subscribe":
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "channel": message.get("channel", "all")
                    })
                    
                else:
                    # Echo back for now
                    await websocket.send_json({
                        "type": "echo",
                        "original": message
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)