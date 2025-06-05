"""Workflow API endpoints for the orchestrator."""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
from loguru import logger

from src.api.base_api import rate_limit
from src.websocket.socket_server import connection_manager


# Request models
class ScenarioRequest(BaseModel):
    """Request model for scenario creation."""
    domain: str
    timeframe: str = "5_years"
    uncertainties: List[str] = []
    
    
class AIEconomyRequest(BaseModel):
    """Request model for AI economy assessment."""
    industry: str
    focus_areas: List[str] = ["automation", "human_agent_collaboration", "new_business_models"]
    

class KnowledgeSynthesisRequest(BaseModel):
    """Request model for knowledge synthesis."""
    domains: List[str]
    objective: str


# Response models
class WorkflowResponse(BaseModel):
    """Response model for workflow initiation."""
    workflow_id: str
    workflow_type: str
    status: str
    created_at: str
    estimated_completion: str


router = APIRouter()


@router.post("/scenario", response_model=WorkflowResponse)
@rate_limit(max_calls=5, window_seconds=60)
async def create_scenario(
    request: ScenarioRequest,
    background_tasks: BackgroundTasks,
    req: Request
):
    """Create future scenarios for a domain."""
    try:
        workflow_id = f"scenario_{uuid.uuid4().hex[:8]}"
        orchestrator = req.app.state.orchestrator
        
        # Start workflow in background
        background_tasks.add_task(
            run_scenario_workflow,
            workflow_id,
            request,
            orchestrator
        )
        
        # Notify clients
        await connection_manager.broadcast_agent_update({
            "event": "workflow:started",
            "workflow_id": workflow_id,
            "workflow_type": "scenario_creation",
            "domain": request.domain
        })
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="scenario_creation",
            status="queued",
            created_at=datetime.now().isoformat(),
            estimated_completion="3-5 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error starting scenario workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-economy", response_model=WorkflowResponse)
@rate_limit(max_calls=5, window_seconds=60)
async def assess_ai_economy(
    request: AIEconomyRequest,
    background_tasks: BackgroundTasks,
    req: Request
):
    """Assess the emerging AI/agent economy for an industry."""
    try:
        workflow_id = f"ai_economy_{uuid.uuid4().hex[:8]}"
        orchestrator = req.app.state.orchestrator
        
        # Start workflow in background
        background_tasks.add_task(
            run_ai_economy_workflow,
            workflow_id,
            request,
            orchestrator
        )
        
        # Notify clients
        await connection_manager.broadcast_agent_update({
            "event": "workflow:started",
            "workflow_id": workflow_id,
            "workflow_type": "ai_economy_assessment",
            "industry": request.industry
        })
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="ai_economy_assessment",
            status="queued",
            created_at=datetime.now().isoformat(),
            estimated_completion="3-5 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error starting AI economy workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-synthesis", response_model=WorkflowResponse)
@rate_limit(max_calls=5, window_seconds=60)
async def synthesize_knowledge(
    request: KnowledgeSynthesisRequest,
    background_tasks: BackgroundTasks,
    req: Request
):
    """Synthesize knowledge across multiple domains."""
    try:
        workflow_id = f"synthesis_{uuid.uuid4().hex[:8]}"
        orchestrator = req.app.state.orchestrator
        
        # Start workflow in background
        background_tasks.add_task(
            run_knowledge_synthesis_workflow,
            workflow_id,
            request,
            orchestrator
        )
        
        # Notify clients
        await connection_manager.broadcast_agent_update({
            "event": "workflow:started",
            "workflow_id": workflow_id,
            "workflow_type": "knowledge_synthesis",
            "domains": request.domains
        })
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="knowledge_synthesis",
            status="queued",
            created_at=datetime.now().isoformat(),
            estimated_completion="4-6 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error starting knowledge synthesis workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str, req: Request):
    """Get the status of a specific workflow."""
    orchestrator = req.app.state.orchestrator
    status = await orchestrator.get_workflow_status(workflow_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return status


@router.get("/active")
async def list_active_workflows(req: Request):
    """List all active workflows."""
    orchestrator = req.app.state.orchestrator
    return await orchestrator.list_active_workflows()


@router.delete("/{workflow_id}")
async def cancel_workflow(workflow_id: str, req: Request):
    """Cancel an active workflow."""
    orchestrator = req.app.state.orchestrator
    success = await orchestrator.cancel_workflow(workflow_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found or already completed")
    
    return {"message": "Workflow cancelled", "workflow_id": workflow_id}


# Background task functions
async def run_scenario_workflow(workflow_id: str, request: ScenarioRequest, orchestrator):
    """Run the scenario creation workflow."""
    try:
        result = await orchestrator.create_scenario(
            domain=request.domain,
            timeframe=request.timeframe,
            uncertainties=request.uncertainties
        )
        
        # Store result (in production, this would go to a database)
        # For now, just log it
        logger.info(f"Scenario workflow {workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Scenario workflow {workflow_id} failed: {e}")
        await connection_manager.broadcast_agent_update({
            "event": "workflow:failed",
            "workflow_id": workflow_id,
            "error": str(e)
        })


async def run_ai_economy_workflow(workflow_id: str, request: AIEconomyRequest, orchestrator):
    """Run the AI economy assessment workflow."""
    try:
        result = await orchestrator.assess_ai_economy(
            industry=request.industry,
            focus_areas=request.focus_areas
        )
        
        logger.info(f"AI economy workflow {workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"AI economy workflow {workflow_id} failed: {e}")
        await connection_manager.broadcast_agent_update({
            "event": "workflow:failed",
            "workflow_id": workflow_id,
            "error": str(e)
        })


async def run_knowledge_synthesis_workflow(workflow_id: str, request: KnowledgeSynthesisRequest, orchestrator):
    """Run the knowledge synthesis workflow."""
    try:
        result = await orchestrator.knowledge_synthesis(
            domains=request.domains,
            objective=request.objective
        )
        
        logger.info(f"Knowledge synthesis workflow {workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Knowledge synthesis workflow {workflow_id} failed: {e}")
        await connection_manager.broadcast_agent_update({
            "event": "workflow:failed",
            "workflow_id": workflow_id,
            "error": str(e)
        })