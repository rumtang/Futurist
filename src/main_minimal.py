"""Minimal main.py for production deployment."""

import os
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting CX Futurist AI system...")
    yield
    logger.info("CX Futurist AI system shut down successfully")

# Create FastAPI app
app = FastAPI(
    title="CX Futurist AI API",
    description="AI-powered customer experience analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "cx-futurist-ai",
            "version": "1.0.0"
        }
    )

# Basic API endpoints
@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    agents = {
        "ai_futurist": {"status": "ready", "description": "AI & Agentic Futurist Agent"},
        "trend_scanner": {"status": "ready", "description": "Trend Scanner Agent"},
        "customer_insight": {"status": "ready", "description": "Customer Insight Agent"},
        "tech_impact": {"status": "ready", "description": "Tech Impact Agent"},
        "org_transformation": {"status": "ready", "description": "Organization Transformation Agent"},
        "synthesis": {"status": "ready", "description": "Synthesis Agent"}
    }
    return {"agents": agents}

@app.post("/api/analysis/analyze")
async def analyze(request_data: dict):
    """Start an analysis."""
    # Simple mock response
    import uuid
    analysis_id = str(uuid.uuid4())
    
    return {
        "analysis_id": analysis_id,
        "status": "started",
        "message": "Analysis started successfully",
        "query": request_data.get("query", ""),
        "analysis_type": request_data.get("analysis_type", "trend_analysis")
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection:established",
            "message": "Connected to CX Futurist AI WebSocket"
        })
        
        # Simple echo server
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
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
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
    # Get port from environment
    port = int(os.environ.get("PORT", 8080))
    
    # Run the application
    uvicorn.run(
        "src.main_minimal:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )