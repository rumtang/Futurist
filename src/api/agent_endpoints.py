"""Agent management API endpoints."""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List
from loguru import logger

from src.api.base_api import rate_limit
from src.websocket.socket_server import connection_manager


router = APIRouter()


@router.get("/status")
async def get_all_agent_status(req: Request) -> Dict[str, Any]:
    """Get the status of all agents."""
    try:
        orchestrator = req.app.state.orchestrator
        agent_states = await orchestrator.get_agent_states()
        
        return {
            "agents": agent_states,
            "total_agents": len(agent_states),
            "timestamp": connection_manager.get_agent_states()
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{agent_name}")
async def get_agent_status(agent_name: str, req: Request) -> Dict[str, Any]:
    """Get the status of a specific agent."""
    try:
        orchestrator = req.app.state.orchestrator
        
        if agent_name not in orchestrator.agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = orchestrator.agents[agent_name]
        
        return {
            "name": agent.name,
            "role": agent.role,
            "status": agent.state.status,
            "current_task": agent.state.current_task,
            "thought_count": len(agent.state.thoughts),
            "message_count": len(agent.state.messages),
            "collaboration_count": len(agent.state.collaborations),
            "last_thoughts": [
                {
                    "content": t.content,
                    "confidence": t.confidence,
                    "timestamp": t.timestamp
                }
                for t in agent.state.thoughts[-5:]  # Last 5 thoughts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thoughts/{agent_name}")
async def get_agent_thoughts(
    agent_name: str, 
    req: Request,
    limit: int = 10,
    min_confidence: float = 0.0
) -> List[Dict[str, Any]]:
    """Get recent thoughts from a specific agent."""
    try:
        orchestrator = req.app.state.orchestrator
        
        if agent_name not in orchestrator.agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = orchestrator.agents[agent_name]
        
        # Filter thoughts by confidence
        thoughts = [
            {
                "content": t.content,
                "confidence": t.confidence,
                "timestamp": t.timestamp,
                "reasoning": t.reasoning_chain
            }
            for t in agent.state.thoughts
            if t.confidence >= min_confidence
        ]
        
        # Sort by timestamp descending and limit
        thoughts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return thoughts[:limit]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent thoughts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collaborations")
async def get_agent_collaborations(req: Request) -> List[Dict[str, Any]]:
    """Get recent collaborations between agents."""
    try:
        orchestrator = req.app.state.orchestrator
        
        all_collaborations = []
        
        for agent_name, agent in orchestrator.agents.items():
            for collab in agent.state.collaborations:
                all_collaborations.append({
                    "from_agent": agent_name,
                    "to_agent": collab["with"],
                    "message": collab["message"],
                    "timestamp": collab["timestamp"],
                    "data": collab.get("data")
                })
        
        # Sort by timestamp descending
        all_collaborations.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return all_collaborations[:50]  # Last 50 collaborations
        
    except Exception as e:
        logger.error(f"Error getting agent collaborations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
@rate_limit(max_calls=1, window_seconds=60)
async def reset_all_agents(req: Request) -> Dict[str, str]:
    """Reset all agents to their initial state."""
    try:
        orchestrator = req.app.state.orchestrator
        await orchestrator.reset_all_agents()
        
        # Notify clients
        await connection_manager.broadcast_agent_update({
            "event": "agents:reset",
            "message": "All agents have been reset"
        })
        
        return {"status": "success", "message": "All agents reset successfully"}
        
    except Exception as e:
        logger.error(f"Error resetting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{agent_name}")
@rate_limit(max_calls=5, window_seconds=60)
async def reset_agent(agent_name: str, req: Request) -> Dict[str, str]:
    """Reset a specific agent to its initial state."""
    try:
        orchestrator = req.app.state.orchestrator
        
        if agent_name not in orchestrator.agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = orchestrator.agents[agent_name]
        await agent.reset_conversation()
        
        # Notify clients
        await connection_manager.broadcast_agent_update({
            "event": "agent:reset",
            "agent": agent_name,
            "message": f"Agent {agent_name} has been reset"
        })
        
        return {"status": "success", "message": f"Agent {agent_name} reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))