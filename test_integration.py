"""
Integration test suite for CX Futurist AI system.

Tests API endpoints, agent initialization, workflows, and WebSocket connectivity.
"""

import asyncio
import httpx
import pytest
import socketio
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime


# Configuration
API_BASE_URL = "http://localhost:8100"
WEBSOCKET_URL = "ws://localhost:8100"
TIMEOUT_SECONDS = 30


class TestSystemIntegration:
    """Integration tests for the CX Futurist AI system."""
    
    @pytest.fixture
    async def api_client(self):
        """Create an async HTTP client."""
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT_SECONDS) as client:
            yield client
    
    @pytest.fixture
    async def socket_client(self):
        """Create a Socket.IO client."""
        sio = socketio.AsyncClient()
        yield sio
        if sio.connected:
            await sio.disconnect()
    
    async def test_api_health_endpoint(self, api_client):
        """Test the /health endpoint."""
        print("Testing health endpoint...")
        response = await api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        
        # Check individual services
        services = data["services"]
        assert services["api"] == "healthy"
        assert services["websocket"] == "healthy"
        assert services["agents"] == "healthy"
        
        print(f"✅ Health check passed: {data}")
    
    async def test_api_root_endpoint(self, api_client):
        """Test the root / endpoint."""
        print("Testing root endpoint...")
        response = await api_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "CX Futurist AI API"
        assert data["version"] == "1.0.0"
        assert data["documentation"] == "/docs"
        
        print(f"✅ Root endpoint passed: {data}")
    
    async def test_api_status_endpoint(self, api_client):
        """Test the /api/status endpoint."""
        print("Testing status endpoint...")
        response = await api_client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "orchestrator" in data
        
        print(f"✅ Status endpoint passed: {data}")
    
    async def test_agent_list_endpoint(self, api_client):
        """Test listing available agents."""
        print("Testing agent list endpoint...")
        response = await api_client.get("/api/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) > 0
        
        # Check for expected agents
        agent_names = [agent["name"] for agent in data["agents"]]
        expected_agents = [
            "ai_futurist",
            "trend_scanner",
            "customer_insight",
            "tech_impact",
            "org_transformation",
            "synthesis"
        ]
        
        for expected in expected_agents:
            assert expected in agent_names, f"Missing expected agent: {expected}"
        
        print(f"✅ Agent list passed: Found {len(agent_names)} agents")
    
    async def test_simple_trend_analysis_workflow(self, api_client):
        """Test a simple trend analysis workflow."""
        print("Testing trend analysis workflow...")
        
        # Start a trend analysis
        request_data = {
            "topic": "AI in customer service",
            "depth": "quick",
            "timeframe": "3-5 years"
        }
        
        response = await api_client.post("/api/analysis/start", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "request_id" in data
        assert "status" in data
        assert data["topic"] == request_data["topic"]
        
        request_id = data["request_id"]
        print(f"✅ Analysis started: {request_id}")
        
        # Poll for completion (with timeout)
        start_time = time.time()
        completed = False
        
        while time.time() - start_time < TIMEOUT_SECONDS:
            status_response = await api_client.get(f"/api/analysis/status/{request_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"  Status: {status_data.get('status', 'unknown')}")
                
                if status_data.get("status") in ["completed", "failed"]:
                    completed = True
                    break
            
            await asyncio.sleep(2)
        
        assert completed, "Analysis did not complete within timeout"
        print(f"✅ Trend analysis workflow completed")
    
    async def test_workflow_creation(self, api_client):
        """Test creating different types of workflows."""
        print("Testing workflow creation...")
        
        # Test scenario creation
        scenario_request = {
            "domain": "retail",
            "timeframe": "5_years",
            "uncertainties": ["AI adoption rate", "privacy regulations"]
        }
        
        response = await api_client.post("/api/workflows/scenario", json=scenario_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "workflow_id" in data
        assert data["workflow_type"] == "scenario_creation"
        assert data["status"] == "queued"
        
        print(f"✅ Scenario workflow created: {data['workflow_id']}")
        
        # Test AI economy assessment
        ai_economy_request = {
            "industry": "healthcare",
            "focus_areas": ["automation", "diagnostics"]
        }
        
        response = await api_client.post("/api/workflows/ai-economy", json=ai_economy_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "workflow_id" in data
        assert data["workflow_type"] == "ai_economy_assessment"
        
        print(f"✅ AI economy workflow created: {data['workflow_id']}")
    
    async def test_websocket_connectivity(self, socket_client):
        """Test WebSocket connection and basic events."""
        print("Testing WebSocket connectivity...")
        
        # Track received events
        received_events = []
        
        @socket_client.on("system:state")
        async def on_system_state(data):
            received_events.append(("system:state", data))
        
        @socket_client.on("agent:update")
        async def on_agent_update(data):
            received_events.append(("agent:update", data))
        
        # Connect to WebSocket
        try:
            await socket_client.connect(f"{WEBSOCKET_URL}/ws")
            assert socket_client.connected
            print("✅ WebSocket connected")
            
            # Wait for initial state
            await asyncio.sleep(2)
            
            # Check if we received system state
            system_state_events = [e for e in received_events if e[0] == "system:state"]
            assert len(system_state_events) > 0, "Did not receive system:state event"
            
            state_data = system_state_events[0][1]
            assert "agents" in state_data
            assert "system" in state_data
            
            print(f"✅ Received system state with {len(state_data['agents'])} agents")
            
            # Test sending a custom event
            await socket_client.emit("ping", {"timestamp": datetime.now().isoformat()})
            
            # Wait a bit for any responses
            await asyncio.sleep(1)
            
        finally:
            if socket_client.connected:
                await socket_client.disconnect()
                print("✅ WebSocket disconnected cleanly")
    
    async def test_api_error_handling(self, api_client):
        """Test API error handling."""
        print("Testing API error handling...")
        
        # Test 404 error
        response = await api_client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404
        
        # Test invalid request data
        invalid_request = {
            "topic": "",  # Empty topic should fail validation
            "depth": "invalid_depth"
        }
        
        response = await api_client.post("/api/analysis/start", json=invalid_request)
        assert response.status_code == 422  # Validation error
        
        print("✅ Error handling working correctly")
    
    async def test_rate_limiting(self, api_client):
        """Test rate limiting on endpoints."""
        print("Testing rate limiting...")
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = await api_client.post(
                "/api/workflows/scenario",
                json={
                    "domain": f"test_domain_{i}",
                    "timeframe": "5_years"
                }
            )
            responses.append(response.status_code)
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.1)
        
        # Check if any requests were rate limited
        rate_limited = any(status == 429 for status in responses)
        
        if rate_limited:
            print("✅ Rate limiting is active")
        else:
            print("⚠️  Rate limiting may not be configured (no 429 responses)")
    
    async def test_metrics_endpoint(self, api_client):
        """Test the metrics endpoint."""
        print("Testing metrics endpoint...")
        
        response = await api_client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "requests_total" in data
        assert "active_analyses" in data
        assert "agent_utilization" in data
        assert "timestamp" in data
        
        print(f"✅ Metrics endpoint passed: {data}")


async def run_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("CX Futurist AI Integration Test Suite")
    print("=" * 60)
    print(f"Testing against: {API_BASE_URL}")
    print()
    
    test_suite = TestSystemIntegration()
    
    # Create clients
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT_SECONDS) as api_client:
        socket_client = socketio.AsyncClient()
        
        try:
            # Run API tests
            print("1. API Health Check")
            await test_suite.test_api_health_endpoint(api_client)
            print()
            
            print("2. API Root Endpoint")
            await test_suite.test_api_root_endpoint(api_client)
            print()
            
            print("3. API Status Endpoint")
            await test_suite.test_api_status_endpoint(api_client)
            print()
            
            print("4. Agent List")
            await test_suite.test_agent_list_endpoint(api_client)
            print()
            
            print("5. Trend Analysis Workflow")
            await test_suite.test_simple_trend_analysis_workflow(api_client)
            print()
            
            print("6. Workflow Creation")
            await test_suite.test_workflow_creation(api_client)
            print()
            
            print("7. WebSocket Connectivity")
            await test_suite.test_websocket_connectivity(socket_client)
            print()
            
            print("8. Error Handling")
            await test_suite.test_api_error_handling(api_client)
            print()
            
            print("9. Rate Limiting")
            await test_suite.test_rate_limiting(api_client)
            print()
            
            print("10. Metrics Endpoint")
            await test_suite.test_metrics_endpoint(api_client)
            print()
            
            print("=" * 60)
            print("✅ All integration tests passed!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            raise
        finally:
            if socket_client.connected:
                await socket_client.disconnect()


if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_integration_tests())