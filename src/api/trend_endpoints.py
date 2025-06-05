"""Trend-specific API endpoints."""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from src.api.base_api import TrendSearchRequest, rate_limit
from src.agents import get_agent
from src.tools.vector_tools import search_trends, store_trend
from src.websocket.socket_server import broadcast_trend_update

router = APIRouter()


# In-memory trend tracking (would use database in production)
active_trends = {}
trend_history = []


@router.get("/active")
async def get_active_trends(
    category: Optional[str] = None,
    min_strength: float = Query(0.5, ge=0.0, le=1.0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get currently active trends."""
    try:
        trends = list(active_trends.values())
        
        # Filter by category
        if category:
            trends = [t for t in trends if t.get("category") == category]
        
        # Filter by strength
        trends = [t for t in trends if t.get("strength", 0) >= min_strength]
        
        # Sort by strength
        trends.sort(key=lambda x: x.get("strength", 0), reverse=True)
        
        # Apply limit
        trends = trends[:limit]
        
        return {
            "trends": trends,
            "count": len(trends),
            "categories": list(set(t.get("category", "general") for t in trends))
        }
        
    except Exception as e:
        logger.error(f"Get active trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weak-signals")
async def get_weak_signals(
    limit: int = Query(10, ge=1, le=50),
    min_potential: float = Query(0.7, ge=0.0, le=1.0)
):
    """Get weak signals with high future potential."""
    try:
        # Get trend scanner agent
        trend_scanner = get_agent("trend_scanner")
        if not trend_scanner:
            raise HTTPException(status_code=503, detail="Trend scanner not available")
        
        # Look for weak signals in active trends
        weak_signals = [
            t for t in active_trends.values()
            if t.get("strength", 0) < 0.5 and t.get("future_potential", 0) >= min_potential
        ]
        
        # Sort by future potential
        weak_signals.sort(key=lambda x: x.get("future_potential", 0), reverse=True)
        
        return {
            "weak_signals": weak_signals[:limit],
            "count": len(weak_signals),
            "scan_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get weak signals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan")
@rate_limit(max_calls=5, window_seconds=300)
async def scan_for_trends(
    request: TrendSearchRequest,
    background_tasks: BackgroundTasks
):
    """Initiate a trend scan."""
    try:
        # Start scan in background
        scan_id = f"scan_{datetime.now().timestamp()}"
        
        background_tasks.add_task(
            run_trend_scan,
            scan_id,
            request
        )
        
        return {
            "scan_id": scan_id,
            "status": "scanning",
            "query": request.query,
            "estimated_completion": "30-60 seconds"
        }
        
    except Exception as e:
        logger.error(f"Scan initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trajectory/{trend_id}")
async def get_trend_trajectory(trend_id: str):
    """Get detailed trajectory analysis for a specific trend."""
    try:
        if trend_id not in active_trends:
            # Try to find in vector database
            results = await search_trends(f"id:{trend_id}", limit=1)
            if not results:
                raise HTTPException(status_code=404, detail="Trend not found")
            
            trend = results[0].get("metadata", {})
        else:
            trend = active_trends[trend_id]
        
        # Generate trajectory analysis
        trajectory = {
            "trend_id": trend_id,
            "name": trend.get("name", "Unknown"),
            "current_strength": trend.get("strength", 0),
            "trajectory_pattern": trend.get("trajectory", "unknown"),
            "momentum": trend.get("momentum", "steady"),
            "historical_data": get_trend_history(trend_id),
            "projections": generate_projections(trend),
            "inflection_points": identify_inflection_points(trend)
        }
        
        return trajectory
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get trajectory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections")
async def get_trend_connections(
    trend_ids: List[str] = Query(...),
    depth: int = Query(1, ge=1, le=3)
):
    """Find connections between specified trends."""
    try:
        if len(trend_ids) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 trends allowed")
        
        connections = []
        
        # Find direct connections
        for i, trend_id1 in enumerate(trend_ids):
            for trend_id2 in trend_ids[i+1:]:
                connection = find_trend_connection(trend_id1, trend_id2)
                if connection:
                    connections.append(connection)
        
        # Find indirect connections if depth > 1
        if depth > 1:
            # Simplified indirect connection finding
            indirect = find_indirect_connections(trend_ids, depth)
            connections.extend(indirect)
        
        return {
            "connections": connections,
            "trend_count": len(trend_ids),
            "connection_count": len(connections),
            "depth": depth
        }
        
    except Exception as e:
        logger.error(f"Get connections error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/{trend_id}")
async def track_trend(trend_id: str, metadata: Optional[Dict[str, Any]] = None):
    """Start tracking a specific trend."""
    try:
        if trend_id in active_trends:
            # Update metadata
            if metadata:
                active_trends[trend_id].update(metadata)
            return {"message": "Trend already being tracked", "trend_id": trend_id}
        
        # Create new trend tracking
        trend = {
            "id": trend_id,
            "name": metadata.get("name", trend_id) if metadata else trend_id,
            "category": metadata.get("category", "general") if metadata else "general",
            "strength": metadata.get("strength", 0.5) if metadata else 0.5,
            "tracking_started": datetime.now().isoformat(),
            "status": "active"
        }
        
        if metadata:
            trend.update(metadata)
        
        active_trends[trend_id] = trend
        
        # Broadcast update
        await broadcast_trend_update({
            "signal": trend["name"],
            "strength": trend["strength"],
            "trajectory": trend.get("trajectory", "stable")
        })
        
        return {"message": "Trend tracking started", "trend": trend}
        
    except Exception as e:
        logger.error(f"Track trend error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/track/{trend_id}")
async def stop_tracking_trend(trend_id: str):
    """Stop tracking a specific trend."""
    try:
        if trend_id not in active_trends:
            raise HTTPException(status_code=404, detail="Trend not found")
        
        trend = active_trends.pop(trend_id)
        
        # Archive to history
        trend["tracking_stopped"] = datetime.now().isoformat()
        trend["status"] = "archived"
        trend_history.append(trend)
        
        return {"message": "Trend tracking stopped", "trend_id": trend_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stop tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_trend_scan(scan_id: str, request: TrendSearchRequest):
    """Run trend scanning in background."""
    try:
        # Get trend scanner agent
        trend_scanner = get_agent("trend_scanner")
        if not trend_scanner:
            logger.error("Trend scanner agent not available")
            return
        
        # Run scan
        results = await trend_scanner.research(request.query)
        
        # Process results
        new_trends = 0
        updated_trends = 0
        
        for trend_type in ["weak_signals", "emerging_trends", "established_trends"]:
            for trend in results.get(trend_type, []):
                trend_id = f"trend_{trend.get('name', '').replace(' ', '_').lower()}"
                
                if trend_id in active_trends:
                    # Update existing trend
                    active_trends[trend_id].update({
                        "strength": trend.get("strength", active_trends[trend_id]["strength"]),
                        "trajectory": trend.get("trajectory", active_trends[trend_id].get("trajectory")),
                        "last_updated": datetime.now().isoformat()
                    })
                    updated_trends += 1
                else:
                    # Add new trend
                    active_trends[trend_id] = {
                        "id": trend_id,
                        "name": trend.get("name", trend.get("title", "Unknown")),
                        "category": request.category or trend.get("category", "general"),
                        "strength": trend.get("strength", 0.5),
                        "trajectory": trend.get("trajectory", "stable"),
                        "type": trend_type.rstrip("s"),  # Remove plural
                        "discovered": datetime.now().isoformat(),
                        "scan_id": scan_id
                    }
                    new_trends += 1
                
                # Store in vector database
                await store_trend(active_trends[trend_id])
        
        logger.info(f"Scan {scan_id} complete: {new_trends} new, {updated_trends} updated")
        
    except Exception as e:
        logger.error(f"Trend scan error: {e}")


def get_trend_history(trend_id: str) -> List[Dict[str, Any]]:
    """Get historical data for a trend."""
    # Simplified - would query time-series database in production
    history = []
    
    # Generate mock historical data
    if trend_id in active_trends:
        trend = active_trends[trend_id]
        current_strength = trend.get("strength", 0.5)
        
        # Generate 30 days of history
        for i in range(30, 0, -1):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            # Simulate gradual increase
            strength = current_strength * (1 - (i / 30) * 0.5)
            history.append({
                "date": date,
                "strength": round(strength, 3),
                "mentions": int(strength * 100)
            })
    
    return history


def generate_projections(trend: Dict[str, Any]) -> Dict[str, Any]:
    """Generate future projections for a trend."""
    current_strength = trend.get("strength", 0.5)
    trajectory = trend.get("trajectory", "stable")
    
    # Simple projection logic
    growth_rates = {
        "exponential": 0.15,
        "linear": 0.05,
        "stable": 0.02,
        "declining": -0.05
    }
    
    growth_rate = growth_rates.get(trajectory, 0.02)
    
    projections = {
        "30_days": min(1.0, current_strength * (1 + growth_rate)),
        "90_days": min(1.0, current_strength * (1 + growth_rate * 3)),
        "180_days": min(1.0, current_strength * (1 + growth_rate * 6)),
        "confidence": 0.7 if trajectory in growth_rates else 0.5
    }
    
    return projections


def identify_inflection_points(trend: Dict[str, Any]) -> List[Dict[str, str]]:
    """Identify potential inflection points for a trend."""
    inflection_points = []
    
    strength = trend.get("strength", 0.5)
    
    # Define inflection thresholds
    if strength < 0.3:
        inflection_points.append({
            "threshold": 0.3,
            "description": "Transition from weak signal to emerging trend",
            "estimated_time": "2-4 weeks"
        })
    
    if strength < 0.7:
        inflection_points.append({
            "threshold": 0.7,
            "description": "Mainstream adoption beginning",
            "estimated_time": "1-3 months"
        })
    
    if strength < 0.9:
        inflection_points.append({
            "threshold": 0.9,
            "description": "Market saturation approaching",
            "estimated_time": "3-6 months"
        })
    
    return inflection_points


def find_trend_connection(trend_id1: str, trend_id2: str) -> Optional[Dict[str, Any]]:
    """Find connection between two trends."""
    if trend_id1 not in active_trends or trend_id2 not in active_trends:
        return None
    
    trend1 = active_trends[trend_id1]
    trend2 = active_trends[trend_id2]
    
    # Simple connection logic
    if trend1.get("category") == trend2.get("category"):
        return {
            "trend1": trend_id1,
            "trend2": trend_id2,
            "connection_type": "same_category",
            "strength": 0.8,
            "description": f"Both in {trend1.get('category')} category"
        }
    
    # Check for convergence potential
    if (trend1.get("strength", 0) > 0.6 and trend2.get("strength", 0) > 0.6 and
        trend1.get("category") != trend2.get("category")):
        return {
            "trend1": trend_id1,
            "trend2": trend_id2,
            "connection_type": "convergence",
            "strength": 0.7,
            "description": "High-strength trends in different domains"
        }
    
    return None


def find_indirect_connections(trend_ids: List[str], depth: int) -> List[Dict[str, Any]]:
    """Find indirect connections between trends."""
    # Simplified implementation
    indirect = []
    
    # Would implement graph traversal in production
    # For now, return empty list
    
    return indirect