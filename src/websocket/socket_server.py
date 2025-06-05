"""WebSocket server for real-time agent communication."""

import asyncio
import json
from typing import Set, Dict, Any, Optional
import socketio
from loguru import logger
from datetime import datetime

from src.config.base_config import settings


# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create ASGI app
socket_app = socketio.ASGIApp(sio, socketio_path='/socket.io/')


class ConnectionManager:
    """Manage WebSocket connections and broadcasts."""
    
    def __init__(self):
        self.active_connections: Set[str] = set()
        self.client_sessions: Dict[str, Dict[str, Any]] = {}
        self.agent_streams: Dict[str, asyncio.Queue] = {}
        
    async def connect(self, sid: str, session_data: Optional[Dict] = None):
        """Handle new connection."""
        self.active_connections.add(sid)
        self.client_sessions[sid] = session_data or {"connected_at": datetime.now().isoformat()}
        logger.info(f"Client {sid} connected. Total connections: {len(self.active_connections)}")
        
        # Send initial state
        await self.send_initial_state(sid)
    
    async def disconnect(self, sid: str):
        """Handle disconnection."""
        self.active_connections.discard(sid)
        self.client_sessions.pop(sid, None)
        logger.info(f"Client {sid} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_initial_state(self, sid: str):
        """Send initial system state to newly connected client."""
        initial_state = {
            "agents": self.get_agent_states(),
            "system": {
                "status": "online",
                "version": "1.0.0",
                "capabilities": [
                    "real-time-streaming",
                    "multi-agent-coordination",
                    "knowledge-graph",
                    "trend-analysis"
                ]
            }
        }
        await sio.emit("system:state", initial_state, room=sid)
    
    def get_agent_states(self) -> Dict[str, Any]:
        """Get current state of all agents."""
        # This will be populated by actual agents
        return {
            "ai_futurist": {"status": "idle", "last_active": None},
            "trend_scanner": {"status": "idle", "last_active": None},
            "customer_insight": {"status": "idle", "last_active": None},
            "tech_impact": {"status": "idle", "last_active": None},
            "org_transformation": {"status": "idle", "last_active": None},
            "synthesis": {"status": "idle", "last_active": None}
        }
    
    async def broadcast_agent_update(self, update: Dict[str, Any]):
        """Broadcast agent updates to all connected clients."""
        await sio.emit("agent:update", update)
    
    async def send_to_client(self, sid: str, event: str, data: Any):
        """Send data to specific client."""
        if sid in self.active_connections:
            await sio.emit(event, data, room=sid)


# Global connection manager
connection_manager = ConnectionManager()


# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection."""
    await connection_manager.connect(sid, auth)
    return True


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    await connection_manager.disconnect(sid)


@sio.event
async def ping(sid):
    """Handle ping for connection keep-alive."""
    await sio.emit("pong", {"timestamp": datetime.now().isoformat()}, room=sid)


@sio.event
async def subscribe(sid, data):
    """Subscribe to specific agent or event streams."""
    subscription_type = data.get("type", "all")
    logger.info(f"Client {sid} subscribing to: {subscription_type}")
    
    # Add client to appropriate rooms
    if subscription_type == "all":
        await sio.enter_room(sid, "all_updates")
    elif subscription_type.startswith("agent:"):
        agent_name = subscription_type.split(":")[1]
        await sio.enter_room(sid, f"agent_{agent_name}")
    
    await sio.emit("subscription:confirmed", {"type": subscription_type}, room=sid)


@sio.event
async def request_analysis(sid, data):
    """Handle analysis request from client."""
    logger.info(f"Analysis request from {sid}: {data}")
    
    # This will trigger the actual analysis workflow
    await sio.emit("analysis:started", {
        "request_id": data.get("id"),
        "status": "processing"
    }, room=sid)
    
    # The actual analysis will be handled by the crews
    # For now, just acknowledge
    return {"status": "accepted", "request_id": data.get("id")}


# Agent streaming callback
async def agent_stream_callback(data: Dict[str, Any]):
    """Callback for agents to stream their updates."""
    event_type = data.get("type")
    agent_name = data.get("agent")
    
    # Map event types to socket events
    event_mapping = {
        "token": "agent:thinking",
        "thought": "agent:thought",
        "state_update": "agent:status",
        "collaboration": "agent:collaboration",
        "insight": "insight:generated",
        "error": "agent:error"
    }
    
    socket_event = event_mapping.get(event_type, "agent:update")
    
    # Broadcast to all interested clients
    await connection_manager.broadcast_agent_update({
        "event": socket_event,
        "agent": agent_name,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })
    
    # Also send to agent-specific rooms
    await sio.emit(socket_event, data, room=f"agent_{agent_name}")


# Knowledge graph updates
async def broadcast_knowledge_update(update: Dict[str, Any]):
    """Broadcast knowledge graph updates."""
    await sio.emit("graph:update", {
        "type": update.get("type", "node_added"),
        "data": update,
        "timestamp": datetime.now().isoformat()
    })


# Trend flow updates
async def broadcast_trend_update(update: Dict[str, Any]):
    """Broadcast trend flow updates."""
    await sio.emit("trend:update", {
        "signal": update.get("signal"),
        "strength": update.get("strength", 0.5),
        "trajectory": update.get("trajectory", "stable"),
        "timestamp": datetime.now().isoformat()
    })


# Scenario updates
async def broadcast_scenario_update(update: Dict[str, Any]):
    """Broadcast scenario evolution updates."""
    await sio.emit("scenario:update", {
        "scenario_id": update.get("id"),
        "branch": update.get("branch"),
        "probability": update.get("probability", 0.5),
        "timestamp": datetime.now().isoformat()
    })


# Export for use in agents
__all__ = [
    'sio',
    'socket_app',
    'connection_manager',
    'agent_stream_callback',
    'broadcast_knowledge_update',
    'broadcast_trend_update',
    'broadcast_scenario_update'
]