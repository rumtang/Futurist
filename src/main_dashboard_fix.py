"""Fixed backend with WebSocket support for dashboard."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Connection manager for WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        
    async def broadcast(self, message: dict):
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Agent states
agent_states = {
    "ai_futurist": {"status": "idle", "last_active": None, "name": "AI & Agentic Futurist"},
    "trend_scanner": {"status": "idle", "last_active": None, "name": "Trend Scanner"},
    "customer_insight": {"status": "idle", "last_active": None, "name": "Customer Insight"},
    "tech_impact": {"status": "idle", "last_active": None, "name": "Tech Impact"},
    "org_transformation": {"status": "idle", "last_active": None, "name": "Org Transformation"},
    "synthesis": {"status": "idle", "last_active": None, "name": "Synthesis"}
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting CX Futurist AI Backend...")
    
    # Start background task to send periodic updates
    task = asyncio.create_task(send_periodic_updates())
    
    yield
    
    # Shutdown
    task.cancel()
    print("Shutting down...")

app = FastAPI(title="CX Futurist AI", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def send_periodic_updates():
    """Send periodic agent status updates."""
    while True:
        try:
            await asyncio.sleep(5)  # Send updates every 5 seconds
            
            # Update a random agent's status
            import random
            agent_id = random.choice(list(agent_states.keys()))
            statuses = ["idle", "thinking", "analyzing", "collaborating"]
            new_status = random.choice(statuses)
            
            agent_states[agent_id]["status"] = new_status
            agent_states[agent_id]["last_active"] = datetime.now().isoformat()
            
            # Broadcast update
            await manager.broadcast({
                "type": "agent:status",
                "agent": agent_id,
                "state": {
                    "status": new_status,
                    "current_task": f"Analyzing trends in {agent_id}" if new_status != "idle" else None
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # Send system state
            await manager.broadcast({
                "type": "system:state",
                "agents": agent_states,
                "system": {
                    "status": "online",
                    "version": "1.0.0",
                    "capabilities": ["real-time-streaming", "multi-agent-coordination"]
                }
            })
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in periodic updates: {e}")

@app.get("/")
async def root():
    return {"message": "CX Futurist AI API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "cx-futurist-ai",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/agents/status")
async def get_agents_status():
    return {
        "agents": {
            agent_id: {
                "status": state["status"],
                "description": state["name"],
                "last_active": state["last_active"]
            }
            for agent_id, state in agent_states.items()
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection:established",
            "message": "Connected to CX Futurist AI",
            "timestamp": datetime.now().isoformat()
        })
        
        # Send current system state
        await websocket.send_json({
            "type": "system:state",
            "agents": agent_states,
            "system": {
                "status": "online",
                "version": "1.0.0",
                "capabilities": ["real-time-streaming", "multi-agent-coordination"]
            }
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
                elif message.get("type") == "subscribe":
                    await websocket.send_json({
                        "type": "subscription:confirmed",
                        "channel": message.get("channel", "all")
                    })
                    
                elif message.get("type") == "request_analysis":
                    # Start mock analysis
                    request_id = f"analysis_{datetime.now().timestamp()}"
                    await websocket.send_json({
                        "type": "analysis:started",
                        "request_id": request_id,
                        "topic": message.get("topic", "general analysis")
                    })
                    
                    # Simulate analysis progress
                    asyncio.create_task(simulate_analysis(websocket, request_id))
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.websocket("/simple-ws")
async def simple_websocket_endpoint(websocket: WebSocket):
    """Simple WebSocket endpoint for compatibility."""
    await websocket_endpoint(websocket)

async def simulate_analysis(websocket: WebSocket, request_id: str):
    """Simulate an analysis with progress updates."""
    try:
        for progress in [20, 40, 60, 80, 100]:
            await asyncio.sleep(2)
            
            if websocket not in manager.active_connections:
                break
                
            await websocket.send_json({
                "type": "analysis:progress",
                "request_id": request_id,
                "progress": progress
            })
            
            # Update agent statuses
            for agent_id in agent_states:
                agent_states[agent_id]["status"] = "analyzing" if progress < 100 else "idle"
                
        if websocket in manager.active_connections:
            await websocket.send_json({
                "type": "analysis:completed",
                "request_id": request_id,
                "results": {
                    "summary": "Analysis completed successfully",
                    "key_insights": [
                        "AI agents are transforming customer service",
                        "Personalization is becoming hyper-targeted",
                        "Voice commerce is growing rapidly"
                    ],
                    "confidence": 0.85
                }
            })
            
    except Exception as e:
        print(f"Error in analysis simulation: {e}")

@app.post("/api/analysis/")
async def start_analysis(data: dict):
    """Start a new analysis."""
    request_id = f"analysis_{datetime.now().timestamp()}"
    
    # Broadcast to all WebSocket clients
    await manager.broadcast({
        "type": "analysis:started",
        "request_id": request_id,
        "topic": data.get("topic", "general analysis")
    })
    
    # Start background analysis
    asyncio.create_task(simulate_analysis_broadcast(request_id))
    
    return {
        "request_id": request_id,
        "status": "started",
        "message": "Analysis started successfully"
    }

async def simulate_analysis_broadcast(request_id: str):
    """Simulate analysis and broadcast updates."""
    for progress in [20, 40, 60, 80, 100]:
        await asyncio.sleep(2)
        await manager.broadcast({
            "type": "analysis:progress",
            "request_id": request_id,
            "progress": progress
        })
    
    await manager.broadcast({
        "type": "analysis:completed",
        "request_id": request_id,
        "results": {
            "summary": "Analysis completed",
            "insights": ["Key insight 1", "Key insight 2"],
            "confidence": 0.9
        }
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)