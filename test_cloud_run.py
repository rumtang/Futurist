#!/usr/bin/env python3
"""Test the simple analysis endpoint on Cloud Run."""

import asyncio
import aiohttp
import json
import sys

async def test_cloud_run():
    """Test the deployed API."""
    base_url = "https://cx-futurist-api-4bgenndxea-uc.a.run.app"
    
    print(f"\n🚀 Testing CX Futurist AI on Cloud Run")
    print(f"📍 URL: {base_url}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Test status endpoint
        print("\n1️⃣ Testing /api/status endpoint...")
        try:
            async with session.get(f"{base_url}/api/status") as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"✅ API Status: {status.get('status', 'unknown')}")
                    print(f"   Services: {status.get('services', {})}")
                else:
                    print(f"❌ Status check failed: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 2. Test simple analysis endpoint
        print("\n2️⃣ Testing /api/simple-analysis/simple endpoint...")
        try:
            async with session.post(
                f"{base_url}/api/simple-analysis/simple",
                json={
                    "topic": "Quick AI test on Cloud Run",
                    "depth": "quick"
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Simple analysis endpoint exists!")
                    print(f"   Request ID: {result.get('request_id')}")
                    print(f"   Status: {result.get('status')}")
                elif response.status == 404:
                    print("❌ Simple analysis endpoint not found (deployment may not be complete)")
                else:
                    print(f"❌ Unexpected status: {response.status}")
                    print(f"   Response: {await response.text()}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 3. Test original analysis endpoint  
        print("\n3️⃣ Testing /api/analysis endpoint...")
        try:
            async with session.post(
                f"{base_url}/api/analysis",
                json={
                    "topic": "Test analysis",
                    "depth": "quick"
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Original analysis endpoint working")
                    print(f"   Request ID: {result.get('request_id')}")
                else:
                    print(f"⚠️  Analysis endpoint status: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_cloud_run())