"""Knowledge base API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from src.api.base_api import KnowledgeSearchRequest, rate_limit
from src.tools.vector_tools import (
    search_insights,
    search_trends, 
    search_all,
    store_insight,
    store_trend,
    pinecone_manager
)
from src.tools.cache_tools import cache_search_results, get_cached_search

router = APIRouter()


@router.post("/search")
@rate_limit(max_calls=20, window_seconds=60)
async def search_knowledge(request: KnowledgeSearchRequest):
    """Search the knowledge base."""
    try:
        # Check cache first
        cache_key = f"{request.query}:{request.limit}"
        cached = await get_cached_search(cache_key)
        if cached:
            return {"results": cached, "cached": True}
        
        # Perform search
        if request.filters and request.filters.get("type"):
            search_type = request.filters["type"]
            if search_type == "insights":
                results = await search_insights(request.query, request.limit)
            elif search_type == "trends":
                results = await search_trends(request.query, request.limit)
            else:
                results = await pinecone_manager.search(request.query, request.limit)
        else:
            # Search all namespaces
            all_results = await search_all(request.query, request.limit)
            results = []
            
            # Combine and sort by score
            for namespace, items in all_results.items():
                for item in items:
                    item["namespace"] = namespace
                    results.append(item)
            
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            results = results[:request.limit]
        
        # Cache results
        await cache_search_results(cache_key, results)
        
        # Format response
        response = {
            "query": request.query,
            "results": results,
            "count": len(results),
            "cached": False
        }
        
        if request.include_metadata:
            response["metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "index_stats": pinecone_manager.get_stats()
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_insights(
    limit: int = Query(20, ge=1, le=100),
    agent: Optional[str] = None,
    confidence_min: float = Query(0.0, ge=0.0, le=1.0)
):
    """Get recent insights."""
    try:
        # Build filter
        filter_dict = {}
        if agent:
            filter_dict["source"] = agent
        
        # Search for recent insights
        results = await pinecone_manager.search(
            query="",  # Empty query for listing
            top_k=limit,
            namespace="insights",
            filter=filter_dict if filter_dict else None
        )
        
        # Filter by confidence if specified
        if confidence_min > 0:
            results = [
                r for r in results 
                if r.get("metadata", {}).get("confidence", 1.0) >= confidence_min
            ]
        
        return {
            "insights": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Get insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trends(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    trajectory: Optional[str] = None
):
    """Get current trends."""
    try:
        # Build filter
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        if trajectory:
            filter_dict["trajectory"] = trajectory
        
        # Search for trends
        results = await pinecone_manager.search(
            query="",  # Empty query for listing
            top_k=limit,
            namespace="trends",
            filter=filter_dict if filter_dict else None
        )
        
        return {
            "trends": results,
            "count": len(results),
            "categories": list(set(r.get("metadata", {}).get("category", "general") for r in results))
        }
        
    except Exception as e:
        logger.error(f"Get trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights")
async def add_insight(insight: Dict[str, Any]):
    """Add a new insight to the knowledge base."""
    try:
        # Validate required fields
        if "content" not in insight:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Add metadata
        insight["timestamp"] = datetime.now().isoformat()
        if "id" not in insight:
            insight["id"] = f"manual_{datetime.now().timestamp()}"
        
        # Store insight
        success = await store_insight(insight)
        
        if success:
            return {"message": "Insight stored successfully", "id": insight["id"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to store insight")
            
    except Exception as e:
        logger.error(f"Add insight error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends")
async def add_trend(trend: Dict[str, Any]):
    """Add a new trend to the knowledge base."""
    try:
        # Validate required fields
        if "name" not in trend:
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Add metadata
        trend["timestamp"] = datetime.now().isoformat()
        if "id" not in trend:
            trend["id"] = f"manual_{datetime.now().timestamp()}"
        
        # Store trend
        success = await store_trend(trend)
        
        if success:
            return {"message": "Trend stored successfully", "id": trend["id"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to store trend")
            
    except Exception as e:
        logger.error(f"Add trend error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics."""
    try:
        stats = pinecone_manager.get_stats()
        
        return {
            "total_vectors": stats.get("total_vector_count", 0),
            "namespaces": stats.get("namespaces", {}),
            "index_fullness": stats.get("index_fullness", 0),
            "dimension": stats.get("dimension", 1536)
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/{namespace}")
async def clear_namespace(namespace: str):
    """Clear all data from a namespace (admin only)."""
    try:
        # In production, this would require authentication
        if namespace not in ["insights", "trends", "documents"]:
            raise HTTPException(status_code=400, detail="Invalid namespace")
        
        # Get all vector IDs in namespace
        # Note: This is a simplified approach, in production you'd paginate
        results = await pinecone_manager.search(
            query="",
            top_k=10000,
            namespace=namespace
        )
        
        if results:
            ids = [r["id"] for r in results]
            success = await pinecone_manager.delete_vectors(ids, namespace=namespace)
            
            if success:
                return {
                    "message": f"Cleared {len(ids)} vectors from {namespace}",
                    "namespace": namespace,
                    "count": len(ids)
                }
        
        return {
            "message": "No vectors to clear",
            "namespace": namespace,
            "count": 0
        }
        
    except Exception as e:
        logger.error(f"Clear namespace error: {e}")
        raise HTTPException(status_code=500, detail=str(e))