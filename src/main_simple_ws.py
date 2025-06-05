"""Modified main.py with simple WebSocket support for testing."""

import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import json

from src.config.base_config import settings
from src.api.base_api import create_app
from src.api.analysis_endpoints import router as analysis_router
from src.api.knowledge_endpoints import router as knowledge_router
from src.api.trend_endpoints import router as trend_router
from src.api.workflow_endpoints import router as workflow_router
from src.api.agent_endpoints import router as agent_router
from src.orchestrator.simple_orchestrator import SimpleOrchestrator

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting CX Futurist AI system...")
    
    # Track which services are available
    app.state.services = {
        "pinecone": False,
        "redis": False,
        "openai": True
    }
    
    # Initialize the simple orchestrator with all agents
    try:
        orchestrator = SimpleOrchestrator()
        app.state.orchestrator = orchestrator
        logger.info("✅ Simple orchestrator and all agents initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}")
        raise
    
    logger.info("🚀 CX Futurist AI system started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 CX Futurist AI system shut down successfully")


# Create main application
app = create_app()
app.router.lifespan_context = lifespan

# Include API routers
app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["Knowledge"])
app.include_router(trend_router, prefix="/api/trends", tags=["Trends"])
app.include_router(workflow_router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(agent_router, prefix="/api/agents", tags=["Agents"])


# Simple WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Simple WebSocket endpoint for testing."""
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection:established",
            "message": "Connected to CX Futurist AI WebSocket"
        })
        
        # Simple echo server for testing
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
                elif message.get("type") == "subscribe":
                    await websocket.send_json({
                        "type": "subscription:confirmed",
                        "channel": message.get("channel", "all")
                    })
                    
                    # Send fake system state
                    await websocket.send_json({
                        "type": "system:state",
                        "agents": {
                            "ai_futurist": {"status": "idle"},
                            "trend_scanner": {"status": "idle"},
                            "customer_insight": {"status": "idle"},
                            "tech_impact": {"status": "idle"},
                            "org_transformation": {"status": "idle"},
                            "synthesis": {"status": "idle"}
                        }
                    })
                    
                else:
                    await websocket.send_json({
                        "type": "echo",
                        "received": message
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")


# Also add /simple-ws endpoint for compatibility
@app.websocket("/simple-ws")
async def simple_ws_endpoint(websocket: WebSocket):
    """Simple WebSocket endpoint matching frontend expectations."""
    await websocket_endpoint(websocket)


if __name__ == "__main__":
    # Get port from environment or use default
    port = settings.cloud_run_port or settings.api_port
    
    # Run the application
    uvicorn.run(
        "src.main_simple_ws:app",
        host=settings.api_host,
        port=port,
        reload=settings.dev_mode,
        log_level=settings.log_level.lower(),
        access_log=True
    )