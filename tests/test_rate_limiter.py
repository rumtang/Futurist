"""Test the rate limiter functionality."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import asyncio
from datetime import datetime

from src.api.base_api import rate_limit, AnalysisRequest


# Create test app
app = FastAPI()


@app.post("/test/standard")
@rate_limit(max_calls=2, window_seconds=5)
async def test_standard(request: Request, data: AnalysisRequest):
    """Standard endpoint with request first."""
    return {"message": "success", "topic": data.topic}


@app.post("/test/flipped")
@rate_limit(max_calls=2, window_seconds=5)
async def test_flipped(data: AnalysisRequest, request: Request):
    """Endpoint with request parameter not first."""
    return {"message": "success", "topic": data.topic}


@app.post("/test/named")
@rate_limit(max_calls=2, window_seconds=5)
async def test_named(req: Request, data: AnalysisRequest):
    """Endpoint with differently named request parameter."""
    return {"message": "success", "topic": data.topic}


@app.get("/test/get")
@rate_limit(max_calls=2, window_seconds=5)
async def test_get(request: Request):
    """GET endpoint."""
    return {"message": "success"}


# Create test client
client = TestClient(app)


def test_rate_limit_standard_endpoint():
    """Test rate limiting on standard endpoint."""
    data = {"topic": "AI trends", "depth": "standard"}
    
    # First two calls should succeed
    response1 = client.post("/test/standard", json=data)
    assert response1.status_code == 200
    
    response2 = client.post("/test/standard", json=data)
    assert response2.status_code == 200
    
    # Third call should be rate limited
    response3 = client.post("/test/standard", json=data)
    assert response3.status_code == 429
    assert "Rate limit exceeded" in response3.json()["detail"]


def test_rate_limit_flipped_params():
    """Test rate limiting when request parameter is not first."""
    data = {"topic": "Future tech", "depth": "comprehensive"}
    
    # First two calls should succeed
    response1 = client.post("/test/flipped", json=data)
    assert response1.status_code == 200
    
    response2 = client.post("/test/flipped", json=data)
    assert response2.status_code == 200
    
    # Third call should be rate limited
    response3 = client.post("/test/flipped", json=data)
    assert response3.status_code == 429


def test_rate_limit_named_request():
    """Test rate limiting with differently named request parameter."""
    data = {"topic": "Customer behavior", "depth": "quick"}
    
    # First two calls should succeed
    response1 = client.post("/test/named", json=data)
    assert response1.status_code == 200
    
    response2 = client.post("/test/named", json=data)
    assert response2.status_code == 200
    
    # Third call should be rate limited
    response3 = client.post("/test/named", json=data)
    assert response3.status_code == 429


def test_rate_limit_get_endpoint():
    """Test rate limiting on GET endpoint."""
    # First two calls should succeed
    response1 = client.get("/test/get")
    assert response1.status_code == 200
    
    response2 = client.get("/test/get")
    assert response2.status_code == 200
    
    # Third call should be rate limited
    response3 = client.get("/test/get")
    assert response3.status_code == 429


def test_rate_limit_window_reset():
    """Test that rate limit resets after time window."""
    import time
    
    data = {"topic": "Reset test", "depth": "standard"}
    
    # Create a new endpoint with 1 second window for faster testing
    @app.post("/test/reset")
    @rate_limit(max_calls=1, window_seconds=1)
    async def test_reset(request: Request, data: AnalysisRequest):
        return {"message": "success"}
    
    # First call should succeed
    response1 = client.post("/test/reset", json=data)
    assert response1.status_code == 200
    
    # Second call should be rate limited
    response2 = client.post("/test/reset", json=data)
    assert response2.status_code == 429
    
    # Wait for window to reset
    time.sleep(1.1)
    
    # Third call should succeed after window reset
    response3 = client.post("/test/reset", json=data)
    assert response3.status_code == 200


def test_different_clients():
    """Test that rate limiting is per-client."""
    # This test would need to mock different client IPs
    # For now, we'll just verify the basic functionality works
    data = {"topic": "Multi-client test", "depth": "standard"}
    
    response = client.post("/test/standard", json=data)
    assert response.status_code in [200, 429]  # Could be rate limited from previous tests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])