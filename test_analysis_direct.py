#!/usr/bin/env python3
"""Test the direct analysis endpoint."""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_direct_analysis():
    """Test the direct analysis endpoint."""
    base_url = "https://cx-futurist-backend-177456512655.us-central1.run.app"
    
    print("Testing Direct Analysis Endpoint...")
    
    # Start analysis
    async with aiohttp.ClientSession() as session:
        # Test 1: Start analysis
        print("\n1. Starting analysis...")
        analysis_data = {
            "topic": "Future of AI agents in customer service",
            "depth": "comprehensive"
        }
        
        async with session.post(f"{base_url}/api/analysis-direct/", json=analysis_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Analysis started: {result['request_id']}")
                request_id = result['request_id']
            else:
                print(f"❌ Failed to start analysis: {resp.status}")
                text = await resp.text()
                print(f"Response: {text}")
                return
        
        # Test 2: Check status
        print("\n2. Checking analysis status...")
        await asyncio.sleep(2)  # Wait a bit
        
        async with session.get(f"{base_url}/api/analysis-direct/{request_id}") as resp:
            if resp.status == 200:
                status = await resp.json()
                print(f"✅ Status: {status['status']}")
                print(f"   Progress: {status.get('progress', 0)}%")
                print(f"   Topic: {status['topic']}")
            else:
                print(f"❌ Failed to get status: {resp.status}")
        
        # Test 3: List analyses
        print("\n3. Listing recent analyses...")
        async with session.get(f"{base_url}/api/analysis-direct/") as resp:
            if resp.status == 200:
                analyses = await resp.json()
                print(f"✅ Found {len(analyses)} analyses")
                for analysis in analyses[:3]:
                    print(f"   - {analysis['request_id']}: {analysis['topic']} ({analysis['status']})")
            else:
                print(f"❌ Failed to list analyses: {resp.status}")
        
        # Test 4: Check agent status
        print("\n4. Checking agent status...")
        async with session.get(f"{base_url}/api/agents/status") as resp:
            if resp.status == 200:
                agents = await resp.json()
                print("✅ Agent statuses:")
                for agent_id, status in agents.items():
                    print(f"   - {agent_id}: {status['status']}")
            else:
                print(f"❌ Failed to get agent status: {resp.status}")

if __name__ == "__main__":
    asyncio.run(test_direct_analysis())