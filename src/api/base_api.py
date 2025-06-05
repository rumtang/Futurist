"""Base API configuration and common endpoints."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from loguru import logger

from src.config.base_config import settings


# Pydantic models for API
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="System status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")
    services: Dict[str, str] = Field(..., description="Service statuses")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


class AnalysisRequest(BaseModel):
    """Request for analysis."""
    topic: str = Field(..., description="Topic to analyze", min_length=3, max_length=500)
    depth: str = Field("comprehensive", description="Analysis depth", pattern="^(quick|standard|comprehensive)$")
    timeframe: str = Field("5-10 years", description="Future timeframe to consider")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class AnalysisResponse(BaseModel):
    """Response from analysis."""
    request_id: str = Field(..., description="Unique request ID")
    status: str = Field(..., description="Analysis status")
    topic: str = Field(..., description="Analyzed topic")
    created_at: str = Field(..., description="Creation timestamp")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class TrendSearchRequest(BaseModel):
    """Request for trend search."""
    query: str = Field(..., description="Search query", min_length=1, max_length=200)
    category: Optional[str] = Field(None, description="Trend category filter")
    timeframe: Optional[str] = Field(None, description="Time range filter")
    min_confidence: float = Field(0.5, description="Minimum confidence score", ge=0, le=1)
    limit: int = Field(10, description="Maximum results", ge=1, le=100)


class KnowledgeSearchRequest(BaseModel):
    """Request for knowledge base search."""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    include_metadata: bool = Field(True, description="Include metadata in results")
    limit: int = Field(20, description="Maximum results", ge=1, le=100)


# Create FastAPI app
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="CX Futurist AI API",
        description="Multi-agent AI system for analyzing the future of customer experience",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "details": str(exc) if settings.dev_mode else None,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        """Check system health and service status."""
        # Check various services
        services = {
            "api": "healthy",
            "websocket": "healthy",
            "agents": "healthy",
            "vector_db": "healthy",
            "redis": "healthy"
        }
        
        # TODO: Implement actual health checks
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            services=services
        )
    
    # Root endpoint
    @app.get("/", tags=["System"])
    async def root():
        """API root endpoint."""
        return {
            "message": "CX Futurist AI API",
            "version": "1.0.0",
            "documentation": "/docs",
            "health": "/health",
            "websocket": "/simple-ws"
        }
    
    # WebSocket health check
    @app.get("/health/websocket", tags=["System"])
    async def websocket_health_check():
        """Health check that includes WebSocket readiness."""
        return {
            "status": "healthy",
            "websocket": {
                "endpoint": "/simple-ws",
                "protocol": "ws",
                "ready": True,
                "features": ["real-time updates", "agent streaming", "analysis progress"]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # Metrics endpoint
    @app.get("/metrics", tags=["System"])
    async def metrics():
        """Get system metrics for monitoring."""
        # TODO: Implement Prometheus metrics
        return {
            "requests_total": 0,
            "active_analyses": 0,
            "agent_utilization": {},
            "timestamp": datetime.now().isoformat()
        }
    
    return app


# Rate limiting decorator
def rate_limit(max_calls: int = 10, window_seconds: int = 60):
    """Rate limiting decorator for endpoints."""
    import functools
    import inspect
    
    call_times: Dict[str, List[float]] = {}
    
    def decorator(func):
        # Get the original function signature
        sig = inspect.signature(func)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the Request object in the arguments
            request = None
            
            # Check positional args first
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Check keyword args if not found
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            # If still no request, check if any parameter is annotated as Request
            if not request:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                for param_name, param in sig.parameters.items():
                    if param.annotation == Request or param_name in ['request', 'req']:
                        if param_name in bound_args.arguments:
                            if isinstance(bound_args.arguments[param_name], Request):
                                request = bound_args.arguments[param_name]
                                break
            
            if not request:
                # If no request found, skip rate limiting
                logger.warning(f"No Request object found in {func.__name__}, skipping rate limit")
                return await func(*args, **kwargs)
            
            client_ip = request.client.host
            current_time = asyncio.get_event_loop().time()
            
            # Clean old entries
            if client_ip in call_times:
                call_times[client_ip] = [
                    t for t in call_times[client_ip] 
                    if current_time - t < window_seconds
                ]
            
            # Check rate limit
            if client_ip in call_times and len(call_times[client_ip]) >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {max_calls} calls per {window_seconds} seconds."
                )
            
            # Record call
            if client_ip not in call_times:
                call_times[client_ip] = []
            call_times[client_ip].append(current_time)
            
            # Execute function with original arguments
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Export models and utilities
__all__ = [
    'create_app',
    'HealthResponse',
    'ErrorResponse',
    'AnalysisRequest',
    'AnalysisResponse',
    'TrendSearchRequest',
    'KnowledgeSearchRequest',
    'rate_limit'
]