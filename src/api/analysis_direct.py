"""Direct analysis execution for Cloud Run compatibility."""

from fastapi import APIRouter, HTTPException
from loguru import logger
import asyncio
from datetime import datetime
from typing import Optional

from src.api.base_api import AnalysisRequest, AnalysisResponse
from src.orchestrator.simple_orchestrator import SimpleOrchestrator
from src.websocket.socket_server import connection_manager

router = APIRouter()

# Store active analyses
active_analyses = {}


@router.post("/")
async def start_analysis_direct(request: AnalysisRequest):
    """Start analysis with direct execution (no background tasks)."""
    try:
        # Generate request ID
        request_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize orchestrator with callback
        async def stream_callback(data):
            await connection_manager.broadcast_agent_update(data)
        
        orchestrator = SimpleOrchestrator(stream_callback=stream_callback)
        
        # Store initial status
        active_analyses[request_id] = {
            "request_id": request_id,
            "status": "running",
            "topic": request.topic,
            "created_at": datetime.now().isoformat(),
            "progress": 0
        }
        
        # Notify start
        await connection_manager.broadcast_agent_update({
            "event": "analysis:started",
            "request_id": request_id,
            "topic": request.topic
        })
        
        # Run analysis directly (not in background)
        asyncio.create_task(run_analysis_async(request_id, request, orchestrator))
        
        return AnalysisResponse(
            request_id=request_id,
            status="running",
            topic=request.topic,
            created_at=datetime.now().isoformat(),
            estimated_completion="2-5 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_analysis_async(request_id: str, request: AnalysisRequest, orchestrator: SimpleOrchestrator):
    """Run analysis asynchronously."""
    try:
        logger.info(f"Starting analysis {request_id} for topic: {request.topic}")
        
        # Update progress
        active_analyses[request_id]["progress"] = 10
        await connection_manager.broadcast_agent_update({
            "event": "analysis:progress",
            "request_id": request_id,
            "progress": 10
        })
        
        # Run the analysis
        result = await orchestrator.analyze_trend(
            topic=request.topic,
            depth=request.depth
        )
        
        # Update with results
        active_analyses[request_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "results": {
                "workflow_id": result.workflow_id,
                "summary": result.results.get("summary"),
                "key_insights": result.results.get("key_insights", []),
                "recommendations": result.results.get("recommendations", []),
                "confidence": result.results.get("confidence", 0.7),
                "agent_outputs": result.agent_outputs
            }
        })
        
        # Notify completion
        await connection_manager.broadcast_agent_update({
            "event": "analysis:completed",
            "request_id": request_id,
            "results": active_analyses[request_id]["results"]
        })
        
        logger.info(f"Analysis {request_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {request_id} failed: {e}")
        
        # Update failure status
        active_analyses[request_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })
        
        # Notify failure
        await connection_manager.broadcast_agent_update({
            "event": "analysis:failed",
            "request_id": request_id,
            "error": str(e)
        })


@router.get("/{request_id}")
async def get_analysis_status_direct(request_id: str):
    """Get analysis status."""
    if request_id not in active_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return active_analyses[request_id]


@router.get("/")
async def list_analyses_direct(limit: int = 10):
    """List recent analyses."""
    analyses = list(active_analyses.values())
    analyses.sort(key=lambda x: x["created_at"], reverse=True)
    return analyses[:limit]