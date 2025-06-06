"""Analysis API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Optional, List
import uuid
from datetime import datetime
from loguru import logger

from src.api.base_api import (
    AnalysisRequest, 
    AnalysisResponse,
    rate_limit
)
from src.agents import get_agent
# from src.tools.cache_tools import cache_analysis_result, get_cached_analysis
from src.websocket.socket_server import connection_manager

router = APIRouter()


# In-memory storage for analysis requests (would use database in production)
analysis_storage = {}


@router.post("/", response_model=AnalysisResponse)
@rate_limit(max_calls=10, window_seconds=60)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    req: Request
):
    """Start a new analysis."""
    try:
        # Generate request ID
        request_id = f"analysis_{uuid.uuid4().hex[:8]}"
        
        # Store request
        analysis_storage[request_id] = {
            "request": request.dict(),
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "results": None
        }
        
        # Get orchestrator from app state
        orchestrator = req.app.state.orchestrator
        
        # Start analysis in background
        background_tasks.add_task(
            run_analysis,
            request_id,
            request,
            orchestrator
        )
        
        # Notify connected clients
        await connection_manager.broadcast_agent_update({
            "event": "analysis:started",
            "request_id": request_id,
            "topic": request.topic
        })
        
        return AnalysisResponse(
            request_id=request_id,
            status="queued",
            topic=request.topic,
            created_at=datetime.now().isoformat(),
            estimated_completion="2-5 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{request_id}")
async def get_analysis_status(request_id: str):
    """Get analysis status and results."""
    # Check storage
    if request_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_storage[request_id]


@router.get("/")
async def list_analyses(
    limit: int = 10,
    status: Optional[str] = None
):
    """List recent analyses."""
    analyses = list(analysis_storage.values())
    
    # Filter by status if provided
    if status:
        analyses = [a for a in analyses if a["status"] == status]
    
    # Sort by creation time
    analyses.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limit results
    return analyses[:limit]


@router.delete("/{request_id}")
async def cancel_analysis(request_id: str):
    """Cancel an analysis."""
    if request_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_storage[request_id]
    
    if analysis["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed analysis")
    
    analysis["status"] = "cancelled"
    
    return {"message": "Analysis cancelled", "request_id": request_id}


async def run_analysis(request_id: str, request: AnalysisRequest, orchestrator):
    """Run the actual analysis using the simple orchestrator."""
    try:
        # Update status
        analysis_storage[request_id]["status"] = "running"
        
        # Notify clients
        await connection_manager.broadcast_agent_update({
            "event": "analysis:progress",
            "request_id": request_id,
            "progress": 10
        })
        
        # Use simple orchestrator instead of CrewAI
        logger.info(f"Starting analysis for topic: {request.topic}")
        
        # Run trend analysis workflow
        workflow_result = await orchestrator.analyze_trend(
            topic=request.topic,
            depth=request.depth
        )
        
        # Update progress to 90%
        await connection_manager.broadcast_agent_update({
            "event": "analysis:progress",
            "request_id": request_id,
            "progress": 90
        })
        
        # Extract results from workflow
        results = {
            "workflow_id": workflow_result.workflow_id,
            "topic": request.topic,
            "summary": workflow_result.results.get("summary"),
            "key_insights": workflow_result.results.get("key_insights", []),
            "recommendations": workflow_result.results.get("recommendations", []),
            "confidence": workflow_result.results.get("confidence", 0.7),
            "agent_outputs": workflow_result.agent_outputs,
            "duration": workflow_result.duration
        }
        
        # Update final status
        analysis_storage[request_id]["status"] = "completed"
        analysis_storage[request_id]["results"] = results
        analysis_storage[request_id]["completed_at"] = datetime.now().isoformat()
        
        # Notify completion
        await connection_manager.broadcast_agent_update({
            "event": "analysis:completed",
            "request_id": request_id,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        
        # Update status
        analysis_storage[request_id]["status"] = "failed"
        analysis_storage[request_id]["error"] = str(e)
        
        # Notify failure
        await connection_manager.broadcast_agent_update({
            "event": "analysis:failed",
            "request_id": request_id,
            "error": str(e)
        })


def determine_agents_for_topic(topic: str) -> List[str]:
    """Determine which agents to use based on the topic."""
    topic_lower = topic.lower()
    
    # Always include these core agents
    agents = ["ai_futurist", "trend_scanner"]
    
    # Add specific agents based on topic
    if any(word in topic_lower for word in ["customer", "cx", "experience", "service"]):
        agents.append("customer_insight")
    
    if any(word in topic_lower for word in ["tech", "technology", "digital", "software"]):
        agents.append("tech_impact")
    
    if any(word in topic_lower for word in ["business", "organization", "company", "enterprise"]):
        agents.append("org_transformation")
    
    # Always include synthesis at the end
    if "synthesis" not in agents:
        agents.append("synthesis")
    
    return agents