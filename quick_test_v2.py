#!/usr/bin/env python3
"""
Quick test to verify basic system functionality.

This is a lightweight test that can be run quickly to verify:
- API is responding
- Agents are initialized
- Basic workflow can be started
"""

import asyncio
import httpx
import sys
from datetime import datetime


async def quick_test():
    """Run a quick system test."""
    print("CX Futurist AI - Quick System Test")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8100"
    all_passed = True
    
    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        # Test 1: Health endpoint
        print("1. Testing health endpoint...")
        try:
            response = await client.get("/health")
            if response.status_code == 200:
                print("   ✅ Health check passed")
            else:
                print(f"   ❌ Health check failed: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            all_passed = False
        
        # Test 2: API status
        print("\n2. Testing API status...")
        try:
            response = await client.get("/api/status")
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                print(f"   ✅ API status: {status}")
                
                # Check services
                services = data.get("services", {})
                for service, available in services.items():
                    icon = "✅" if available else "⚠️"
                    print(f"     {icon} {service}: {'available' if available else 'not configured'}")
            else:
                print(f"   ❌ Status check failed: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
            all_passed = False
        
        # Test 3: List agents
        print("\n3. Testing agent availability...")
        try:
            response = await client.get("/api/agents/status")
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", {})
                print(f"   ✅ Found {len(agents)} agents:")
                for agent_name, agent_data in list(agents.items())[:6]:
                    status = agent_data.get('status', 'unknown')
                    print(f"     - {agent_name}: {status}")
            else:
                print(f"   ❌ Agent list failed: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Agent list error: {e}")
            all_passed = False
        
        # Test 4: Start a simple analysis
        print("\n4. Testing analysis creation...")
        try:
            request_data = {
                "topic": "AI agents transforming customer service",
                "scope": "emerging_trends",
                "priority": "normal"
            }
            
            response = await client.post("/api/analysis/", json=request_data)
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id", "unknown")
                status = data.get("status", "unknown")
                print(f"   ✅ Analysis started: {request_id}")
                print(f"   ✅ Status: {status}")
            else:
                print(f"   ❌ Analysis creation failed: HTTP {response.status_code}")
                if response.status_code == 422:
                    print(f"      Error: {response.text}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Analysis test error: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ ALL TESTS PASSED - System is ready!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check the errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(quick_test())
    sys.exit(exit_code)