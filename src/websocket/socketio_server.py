"""Socket.IO WebSocket server implementation."""

import asyncio
import socketio
from loguru import logger
from datetime import datetime
import json
from typing import Dict, Any, Optional

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Allow all origins in production
    logger=False,
    engineio_logger=False
)

# Create ASGI app
socket_app = socketio.ASGIApp(
    sio,
    socketio_path='/ws/socket.io/'
)

# Store client subscriptions
client_subscriptions: Dict[str, set] = {}

@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client {sid} connected")
    client_subscriptions[sid] = set()
    
    # Send initial connection confirmation
    await sio.emit('connection:established', {
        'connected': True,
        'sid': sid,
        'timestamp': datetime.now().isoformat()
    }, to=sid)
    
    # Send initial system state
    await send_system_state(sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client {sid} disconnected")
    if sid in client_subscriptions:
        del client_subscriptions[sid]

@sio.event
async def ping(sid):
    """Handle ping request."""
    await sio.emit('pong', {'timestamp': datetime.now().isoformat()}, to=sid)

@sio.event
async def subscribe(sid, data):
    """Handle subscription request."""
    subscription_type = data.get('type', 'all')
    
    if sid in client_subscriptions:
        client_subscriptions[sid].add(subscription_type)
    
    # Send subscription confirmation
    await sio.emit('subscription:confirmed', {
        'type': subscription_type,
        'timestamp': datetime.now().isoformat()
    }, to=sid)
    
    logger.info(f"Client {sid} subscribed to {subscription_type}")

@sio.event
async def unsubscribe(sid, data):
    """Handle unsubscription request."""
    subscription_type = data.get('type', 'all')
    
    if sid in client_subscriptions:
        client_subscriptions[sid].discard(subscription_type)
    
    logger.info(f"Client {sid} unsubscribed from {subscription_type}")

@sio.event
async def request_analysis(sid, data):
    """Handle analysis request."""
    logger.info(f"Analysis requested by {sid}: {data}")
    
    # Send analysis started event
    await sio.emit('analysis:started', {
        'id': data.get('id'),
        'topic': data.get('topic'),
        'timestamp': datetime.now().isoformat()
    }, to=sid)
    
    # TODO: Integrate with actual orchestrator
    # For now, send mock progress updates
    await asyncio.sleep(1)
    
    await sio.emit('analysis:progress', {
        'id': data.get('id'),
        'progress': 50,
        'message': 'Analyzing trends...',
        'timestamp': datetime.now().isoformat()
    }, to=sid)
    
    await asyncio.sleep(1)
    
    await sio.emit('analysis:completed', {
        'id': data.get('id'),
        'results': {
            'summary': 'Analysis complete',
            'insights': ['Insight 1', 'Insight 2']
        },
        'timestamp': datetime.now().isoformat()
    }, to=sid)

async def send_system_state(sid: Optional[str] = None):
    """Send current system state."""
    state = {
        'agents': {
            'ai_futurist': {'status': 'idle', 'last_active': None},
            'trend_scanner': {'status': 'idle', 'last_active': None},
            'customer_insight': {'status': 'idle', 'last_active': None},
            'tech_impact': {'status': 'idle', 'last_active': None},
            'org_transformation': {'status': 'idle', 'last_active': None},
            'synthesis': {'status': 'idle', 'last_active': None}
        },
        'system': {
            'status': 'operational',
            'version': '1.0.0',
            'capabilities': ['analysis', 'real-time', 'multi-agent']
        }
    }
    
    event_data = {
        'type': 'system:state',
        'data': state,
        'timestamp': datetime.now().isoformat()
    }
    
    if sid:
        await sio.emit('system:state', event_data, to=sid)
    else:
        await sio.emit('system:state', event_data)

async def broadcast_agent_update(agent_name: str, event: str, data: Any):
    """Broadcast agent update to all subscribed clients."""
    update = {
        'agent': agent_name,
        'event': event,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    # Send to all clients subscribed to 'all' or specific agent
    for sid, subscriptions in client_subscriptions.items():
        if 'all' in subscriptions or agent_name in subscriptions:
            await sio.emit('agent:update', update, to=sid)

async def broadcast_insight(insight_data: Dict[str, Any]):
    """Broadcast new insight to all clients."""
    await sio.emit('insight:generated', {
        'data': insight_data,
        'timestamp': datetime.now().isoformat()
    })

# Export the server and app
__all__ = ['sio', 'socket_app', 'broadcast_agent_update', 'broadcast_insight']