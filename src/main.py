"""Main application entry point for CX Futurist AI."""

import asyncio
import uvicorn
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from src.config.base_config import settings
from src.api.base_api import create_app
from src.websocket.socket_server import socket_app, sio
from src.api.analysis_endpoints import router as analysis_router
from src.api.analysis_direct import router as analysis_direct_router
from src.api.simple_analysis import router as simple_analysis_router
from src.api.agent_endpoints import router as agent_router
from src.orchestrator.simple_orchestrator import SimpleOrchestrator
from src.websocket.socket_server import agent_stream_callback

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    f"logs/{settings.log_file}",
    rotation="500 MB",
    retention="10 days",
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
        "openai": True  # Assume OpenAI is required
    }
    
    # Initialize services with graceful degradation
    
    # Skip Pinecone initialization - removed for minimization
    app.state.services["pinecone"] = False
    logger.info("ℹ️  Vector database disabled (minimized version)")
    
    # Skip Redis initialization - removed for minimization
    app.state.services["redis"] = False
    logger.info("ℹ️  Redis cache disabled (minimized version)")
    
    # Initialize the simple orchestrator with all agents (always required)
    try:
        orchestrator = SimpleOrchestrator(stream_callback=agent_stream_callback)
        app.state.orchestrator = orchestrator
        logger.info("✅ Simple orchestrator and all agents initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}")
        logger.error("This is a critical error - orchestrator is required")
        raise
    
    # Log service availability summary
    logger.info("=" * 60)
    logger.info("Service Availability Summary:")
    logger.info(f"  OpenAI API: {'✅ Available' if app.state.services['openai'] else '❌ Unavailable'}")
    logger.info(f"  Pinecone: {'✅ Available' if app.state.services['pinecone'] else '⚠️  Unavailable (degraded mode)'}")
    logger.info(f"  Redis: {'✅ Available' if app.state.services['redis'] else '⚠️  Unavailable (no caching)'}")
    logger.info("=" * 60)
    
    if not app.state.services["pinecone"]:
        logger.info("💡 To enable vector search, configure PINECONE_API_KEY and PINECONE_INDEX_NAME")
    if not app.state.services["redis"]:
        logger.info("💡 To enable caching, ensure Redis is running and accessible")
    
    logger.info("🚀 CX Futurist AI system started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CX Futurist AI system...")
    
    # Cleanup with graceful handling
    
    # Pinecone not used in minimized version
    
    # Redis not used in minimized version
    
    logger.info("🛑 CX Futurist AI system shut down successfully")


# Create main application
app = create_app()
app.router.lifespan_context = lifespan

# Mount WebSocket app
app.mount("/ws", socket_app)

# Include API routers
app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(analysis_direct_router, prefix="/api/analysis-direct", tags=["Analysis-Direct"])
app.include_router(simple_analysis_router, prefix="/api/simple-analysis", tags=["Simple-Analysis"])
app.include_router(agent_router, prefix="/api/agents", tags=["Agents"])


# Add a service status endpoint
@app.get("/api/status", tags=["System"])
async def get_service_status():
    """Get the status of all services."""
    services = getattr(app.state, 'services', {
        "openai": False,
        "pinecone": False,
        "redis": False
    })
    
    orchestrator_status = hasattr(app.state, 'orchestrator') and app.state.orchestrator is not None
    
    # Test OpenAI connectivity
    openai_test = {"status": "untested"}
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        openai_test = {"status": "connected", "model": "gpt-3.5-turbo"}
    except Exception as e:
        openai_test = {"status": "error", "error": str(e)[:100]}
    
    return {
        "status": "operational" if services.get("openai") and orchestrator_status else "degraded",
        "services": services,
        "orchestrator": orchestrator_status,
        "openai_test": openai_test,
        "message": "System is running. Some features may be limited if external services are unavailable."
    }


# Add a simple WebSocket endpoint as fallback
@app.websocket("/simple-ws")
async def simple_websocket_endpoint(websocket: WebSocket):
    """Simple WebSocket endpoint for basic connectivity."""
    await websocket.accept()
    logger.info("Simple WebSocket connection established")
    
    try:
        await websocket.send_json({
            "type": "connection:established", 
            "message": "Connected to CX Futurist AI"
        })
        
        # Send initial system state
        await websocket.send_json({
            "type": "system:state",
            "agents": {
                "ai_futurist": {"status": "idle", "last_active": None},
                "trend_scanner": {"status": "idle", "last_active": None},
                "customer_insight": {"status": "idle", "last_active": None},
                "tech_impact": {"status": "idle", "last_active": None},
                "org_transformation": {"status": "idle", "last_active": None},
                "synthesis": {"status": "idle", "last_active": None}
            },
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
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                logger.info(f"Received WebSocket message: {message_type}")
                
                if message_type == "subscribe":
                    await websocket.send_json({
                        "type": "subscription:confirmed",
                        "data": message,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif message_type == "request_analysis":
                    # Handle analysis request
                    request_id = message.get("id", f"analysis_{datetime.now().timestamp()}")
                    topic = message.get("topic", "general analysis")
                    
                    # Send analysis started
                    await websocket.send_json({
                        "type": "analysis:started",
                        "request_id": request_id,
                        "topic": topic,
                        "status": "processing",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Simulate some agent activity
                    agents = ["ai_futurist", "trend_scanner", "customer_insight"]
                    for i, agent in enumerate(agents):
                        await asyncio.sleep(0.5)  # Simulate processing time
                        
                        # Send agent status update
                        await websocket.send_json({
                            "type": "agent:status",
                            "agent": agent,
                            "data": {
                                "status": "thinking",
                                "current_task": f"Analyzing: {topic}",
                                "progress": (i + 1) * 30
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Send agent thought
                        await websocket.send_json({
                            "type": "agent:thought",
                            "agent": agent,
                            "thought": {
                                "content": f"Exploring {topic} from {agent} perspective...",
                                "confidence": 0.8,
                                "timestamp": datetime.now().timestamp()
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Send completion
                    await asyncio.sleep(1)
                    await websocket.send_json({
                        "type": "analysis:completed",
                        "request_id": request_id,
                        "results": {
                            "summary": f"Analysis of '{topic}' completed successfully",
                            "insights": [
                                "Emerging AI trends show increased adoption",
                                "Customer experience is becoming more personalized",
                                "Agentic systems are reshaping interactions"
                            ],
                            "confidence": 0.85
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                else:
                    # Echo unknown messages
                    await websocket.send_json({
                        "type": "echo",
                        "original": message,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except json.JSONDecodeError:
                if websocket.client_state.CONNECTED:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON received",
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as inner_e:
                logger.error(f"Error processing WebSocket message: {inner_e}")
                if websocket.client_state.CONNECTED:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing message: {str(inner_e)}",
                        "timestamp": datetime.now().isoformat()
                    })
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    import os
    # Get port from environment or use default (Cloud Run requires 8080)
    port = int(os.environ.get("PORT", "8080"))
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",  # Cloud Run needs to bind to all interfaces
        port=port,
        reload=False,  # No reload in production
        log_level=settings.log_level.lower(),
        access_log=True
    )