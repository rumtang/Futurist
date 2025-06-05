"""Production-optimized main application for CX Futurist AI with WebSocket support."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

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


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


# Global connection manager
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("🚀 Starting CX Futurist AI Production Backend...")
    
    # Initialize service availability
    app.state.services = {
        "openai": bool(settings.openai_api_key),
        "websocket": True,
        "agents": True
    }
    
    # Simple agent state for demo
    app.state.agents = {
        "ai_futurist": {"status": "idle", "last_active": None},
        "trend_scanner": {"status": "idle", "last_active": None},
        "customer_insight": {"status": "idle", "last_active": None},
        "tech_impact": {"status": "idle", "last_active": None},
        "org_transformation": {"status": "idle", "last_active": None},
        "synthesis": {"status": "idle", "last_active": None}
    }
    
    logger.info(f"✅ Services initialized: {app.state.services}")
    logger.info("🌐 WebSocket endpoint available at /ws and /simple-ws")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CX Futurist AI Production Backend...")


# Create FastAPI app
app = FastAPI(
    title="CX Futurist AI Backend",
    description="Production-optimized backend with WebSocket support",
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
            "websocket": "/ws or /simple-ws"
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
    agents = getattr(app.state, 'agents', {})
    
    return {
        "status": "operational",
        "services": services,
        "agents": agents,
        "websocket_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }


async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "ping":
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })
    
    elif message_type == "subscribe":
        channel = message.get("channel", "all")
        await websocket.send_json({
            "type": "subscription:confirmed",
            "channel": channel,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send current system state
        await websocket.send_json({
            "type": "system:state",
            "agents": app.state.agents,
            "services": app.state.services,
            "timestamp": datetime.now().isoformat()
        })
    
    elif message_type == "request_analysis":
        # Simulate analysis workflow
        request_id = message.get("id", f"analysis_{datetime.now().timestamp()}")
        topic = message.get("topic", "general analysis")
        
        await websocket.send_json({
            "type": "analysis:started",
            "request_id": request_id,
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate agent activity
        agents = ["ai_futurist", "trend_scanner", "customer_insight"]
        for agent in agents:
            await asyncio.sleep(0.5)
            
            # Update agent state
            app.state.agents[agent]["status"] = "thinking"
            app.state.agents[agent]["last_active"] = datetime.now().isoformat()
            
            # Send status update
            await websocket.send_json({
                "type": "agent:status",
                "agent": agent,
                "data": {
                    "status": "thinking",
                    "current_task": f"Analyzing {topic}",
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Send agent thought
            await websocket.send_json({
                "type": "agent:thought",
                "agent": agent,
                "thought": {
                    "content": f"{agent} is processing: {topic}",
                    "confidence": 0.85
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # Reset agent status
            app.state.agents[agent]["status"] = "idle"
        
        # Send completion
        await websocket.send_json({
            "type": "analysis:completed",
            "request_id": request_id,
            "results": {
                "summary": f"Analysis of '{topic}' completed",
                "insights": [
                    "AI adoption is accelerating across industries",
                    "Customer expectations are evolving rapidly",
                    "Agentic systems show promising results"
                ],
                "confidence": 0.9
            },
            "timestamp": datetime.now().isoformat()
        })
    
    else:
        # Echo unknown messages
        await websocket.send_json({
            "type": "echo",
            "original": message,
            "timestamp": datetime.now().isoformat()
        })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint."""
    await manager.connect(websocket)
    
    try:
        # Send connection established message
        await websocket.send_json({
            "type": "connection:established",
            "message": "Connected to CX Futurist AI WebSocket",
            "timestamp": datetime.now().isoformat()
        })
        
        # Message handling loop
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.websocket("/simple-ws")
async def simple_websocket_endpoint(websocket: WebSocket):
    """Alternative WebSocket endpoint for compatibility."""
    await websocket_endpoint(websocket)


# Basic API endpoints for testing
@app.post("/api/analysis/start")
async def start_analysis(topic: str = "emerging AI trends"):
    """Start an analysis and broadcast to WebSocket clients."""
    analysis_id = f"analysis_{datetime.now().timestamp()}"
    
    # Broadcast to all connected clients
    await manager.broadcast({
        "type": "analysis:broadcast",
        "analysis_id": analysis_id,
        "topic": topic,
        "status": "started",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "analysis_id": analysis_id,
        "topic": topic,
        "status": "started",
        "websocket_clients": len(manager.active_connections)
    }


@app.get("/api/agents")
async def get_agents():
    """Get all agent states."""
    return {
        "agents": app.state.agents,
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