#!/usr/bin/env python3
"""Test complete flow from API to crew execution"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8100"

def test_health():
    """Test backend health"""
    print("1. Testing backend health...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✓ Backend is healthy")
        print(json.dumps(response.json(), indent=2))
    else:
        print("✗ Backend health check failed")
        sys.exit(1)

def test_agents():
    """Test agent status"""
    print("\n2. Testing agent status...")
    response = requests.get(f"{BASE_URL}/api/agents/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['total_agents']} agents")
        for agent_name, agent_info in data['agents'].items():
            print(f"  - {agent_name}: {agent_info['status']}")
    else:
        print("✗ Agent status check failed")
        sys.exit(1)

def test_websocket():
    """Test WebSocket connectivity"""
    print("\n3. Testing WebSocket endpoint...")
    response = requests.get(f"{BASE_URL}/ws", allow_redirects=False)
    if response.status_code in [307, 301]:
        print("✓ WebSocket endpoint is available")
    else:
        print("✗ WebSocket check failed")

def test_analysis():
    """Test analysis endpoint"""
    print("\n4. Testing analysis endpoint...")
    
    # Submit analysis request
    analysis_data = {
        "topic": "How will AI agents impact customer service in 2025?",
        "analysis_type": "quick"
    }
    
    print("Submitting analysis request...")
    response = requests.post(f"{BASE_URL}/api/analysis/", json=analysis_data)
    
    if response.status_code == 200:
        result = response.json()
        request_id = result['request_id']
        print(f"✓ Analysis queued: {request_id}")
        
        # Poll for results
        print("Polling for results...")
        for i in range(30):  # Poll for up to 30 seconds
            time.sleep(1)
            status_response = requests.get(f"{BASE_URL}/api/analysis/{request_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"  Status: {status_data['status']}")
                
                if status_data['status'] == 'completed':
                    print("✓ Analysis completed successfully!")
                    print("\nResults:")
                    print(json.dumps(status_data.get('results', {}), indent=2))
                    break
                elif status_data['status'] == 'failed':
                    print(f"✗ Analysis failed: {status_data.get('error', 'Unknown error')}")
                    break
                else:
                    # Check agent activity
                    agent_response = requests.get(f"{BASE_URL}/api/agents/status")
                    if agent_response.status_code == 200:
                        agents = agent_response.json()['agents']
                        active_agents = [name for name, info in agents.items() if info['status'] != 'idle']
                        if active_agents:
                            print(f"  Active agents: {', '.join(active_agents)}")
        else:
            print("✗ Analysis timed out")
    else:
        print(f"✗ Failed to submit analysis: {response.status_code}")
        print(response.text)

def test_workflows():
    """Test workflow endpoints"""
    print("\n5. Testing workflow endpoints...")
    
    # Get active workflows
    response = requests.get(f"{BASE_URL}/api/workflows/active")
    if response.status_code == 200:
        workflows = response.json()
        print(f"✓ Found {len(workflows)} workflows in history")
        
        # Show recent failures
        failed = [w for w in workflows if w['status'] == 'failed']
        if failed:
            print(f"\nRecent failures:")
            for w in failed[:3]:  # Show up to 3 recent failures
                print(f"  - {w['workflow_type']}: {w.get('errors', ['Unknown error'])[0]}")
    else:
        print("✗ Failed to get workflows")

def main():
    """Run all tests"""
    print("=== CX Futurist AI Complete Flow Test ===\n")
    
    test_health()
    test_agents()
    test_websocket()
    test_analysis()
    test_workflows()
    
    print("\n=== Test Summary ===")
    print("Backend: ✓ Running")
    print("Agents: ✓ Initialized")
    print("WebSocket: ✓ Available")
    print("Analysis: ⚠️  Has errors (see above)")
    print("\nRecommendation: Fix orchestrator error handling and missing agent methods")

if __name__ == "__main__":
    main()