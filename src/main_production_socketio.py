"""Production-optimized main application with Socket.IO support."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os
import socketio

# Simplified config for production
class Settings:
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    cloud_run_port: int = int(os.environ.get("PORT", "8080"))
    log_level: str = "INFO"
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    
settings = Settings()

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Allow all origins in production
    logger=False,
    engineio_logger=False
)

# Create ASGI app for Socket.IO
socket_app = socketio.ASGIApp(
    sio,
    socketio_path='/socket.io/'
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
async def request_analysis(sid, data):
    """Handle analysis request."""
    logger.info(f"Analysis requested by {sid}: {data}")
    
    request_id = data.get('id', f"analysis_{datetime.now().timestamp()}")
    topic = data.get('topic', 'general analysis')
    
    # Send analysis started event
    await sio.emit('analysis:started', {
        'id': request_id,
        'topic': topic,
        'timestamp': datetime.now().isoformat()
    }, to=sid)
    
    # Simulate agent activity
    agents = ["ai_futurist", "trend_scanner", "customer_insight"]
    for i, agent in enumerate(agents):
        await asyncio.sleep(0.5)
        
        # Send agent status update
        await sio.emit('agent:status', {
            'agent': agent,
            'data': {
                'status': 'thinking',
                'current_task': f'Analyzing {topic}',
                'timestamp': datetime.now().isoformat()
            }
        }, to=sid)
        
        # Send agent thought
        await sio.emit('agent:thought', {
            'agent': agent,
            'thought': {
                'content': f'{agent} is processing: {topic}',
                'confidence': 0.85
            },
            'timestamp': datetime.now().isoformat()
        }, to=sid)
        
        # Send progress update
        await sio.emit('analysis:progress', {
            'id': request_id,
            'progress': int((i + 1) / len(agents) * 100),
            'message': f'{agent} completed analysis',
            'timestamp': datetime.now().isoformat()
        }, to=sid)
    
    # Send completion
    await sio.emit('analysis:completed', {
        'id': request_id,
        'results': {
            'summary': f"Analysis of '{topic}' completed",
            'insights': [
                'AI adoption is accelerating across industries',
                'Customer expectations are evolving rapidly',
                'Agentic systems show promising results'
            ],
            'confidence': 0.9
        },
        'timestamp': datetime.now().isoformat()
    }, to=sid)

async def send_system_state(sid=None):
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
    
    if sid:
        await sio.emit('system:state', state, to=sid)
    else:
        await sio.emit('system:state', state)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("🚀 Starting CX Futurist AI Production Backend with Socket.IO...")
    
    # Initialize service availability
    app.state.services = {
        "openai": bool(settings.openai_api_key),
        "websocket": True,
        "agents": True
    }
    
    logger.info(f"✅ Services initialized: {app.state.services}")
    logger.info("🌐 Socket.IO endpoint available at /ws/socket.io/")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CX Futurist AI Production Backend...")

# Create FastAPI app
app = FastAPI(
    title="CX Futurist AI Backend",
    description="Production-optimized backend with Socket.IO support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app
app.mount("/ws", socket_app)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "CX Futurist AI Backend",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/api/status",
            "websocket": "/ws/socket.io/"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def get_service_status():
    """Get the status of all services."""
    services = getattr(app.state, 'services', {})
    
    return {
        "status": "operational",
        "services": services,
        "websocket_connections": len(client_subscriptions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analysis/start")
async def start_analysis(topic: str = "emerging AI trends"):
    """Start an analysis and broadcast to Socket.IO clients."""
    analysis_id = f"analysis_{datetime.now().timestamp()}"
    
    # Broadcast to all connected clients
    await sio.emit('analysis:broadcast', {
        'analysis_id': analysis_id,
        'topic': topic,
        'status': 'started',
        'timestamp': datetime.now().isoformat()
    })
    
    return {
        "analysis_id": analysis_id,
        "topic": topic,
        "status": "started",
        "websocket_clients": len(client_subscriptions)
    }

@app.get("/api/agents/status")
async def get_agents_status():
    """Get all agent states."""
    return {
        "total_agents": 6,
        "agents": {
            "ai_futurist": {"status": "idle", "capabilities": ["AI trend analysis", "Agent evolution"]},
            "trend_scanner": {"status": "idle", "capabilities": ["Weak signal detection", "Pattern recognition"]},
            "customer_insight": {"status": "idle", "capabilities": ["Behavior analysis", "Experience prediction"]},
            "tech_impact": {"status": "idle", "capabilities": ["Technology assessment", "Impact analysis"]},
            "org_transformation": {"status": "idle", "capabilities": ["Change prediction", "Adaptation strategies"]},
            "synthesis": {"status": "idle", "capabilities": ["Insight integration", "Scenario creation"]}
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Get port from environment
    port = settings.cloud_run_port or settings.api_port
    
    # Run the application
    uvicorn.run(
        app,
        host=settings.api_host,
        port=port,
        log_level=settings.log_level.lower(),
        access_log=True
    )