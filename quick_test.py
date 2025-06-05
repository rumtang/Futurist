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
                print("   Services:")
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
            response = await client.get("/api/agents")
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                print(f"   ✅ Found {len(agents)} agents:")
                for agent in agents[:6]:  # Show first 6
                    print(f"     - {agent['name']}")
                if len(agents) > 6:
                    print(f"     ... and {len(agents) - 6} more")
            else:
                print(f"   ❌ Agent list failed: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Agent list error: {e}")
            all_passed = False
        
        # Test 4: Start a simple workflow
        print("\n4. Testing workflow creation...")
        try:
            request_data = {
                "topic": "Quick test analysis",
                "depth": "quick",
                "timeframe": "1 year"
            }
            
            response = await client.post("/api/analysis/start", json=request_data)
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id", "unknown")
                print(f"   ✅ Workflow started: {request_id}")
                
                # Wait and check status
                await asyncio.sleep(1)
                status_response = await client.get(f"/api/analysis/status/{request_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   ✅ Workflow status: {status_data.get('status', 'unknown')}")
                else:
                    print(f"   ⚠️  Could not check workflow status")
            else:
                print(f"   ❌ Workflow creation failed: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Workflow test error: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ ALL TESTS PASSED - System is operational!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check the errors above")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(quick_test())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        print("\nIs the server running? Start it with: python -m src.main")
        sys.exit(1)