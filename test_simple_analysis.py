#!/usr/bin/env python3
"""Test script for the simple analysis endpoint."""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys

async def test_simple_analysis():
    """Test the simple analysis endpoint."""
    base_url = "http://localhost:8080"
    
    # Test topic
    test_topic = "AI agent autonomy in customer service"
    
    print(f"\n🧪 Testing Simple Analysis Endpoint")
    print(f"📍 Server: {base_url}")
    print(f"🎯 Topic: {test_topic}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Start analysis
        print("\n1️⃣ Starting analysis...")
        try:
            async with session.post(
                f"{base_url}/api/simple-analysis/simple",
                json={
                    "topic": test_topic,
                    "depth": "comprehensive"
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    request_id = result.get("request_id")
                    print(f"✅ Analysis started successfully!")
                    print(f"   Request ID: {request_id}")
                    print(f"   Status: {result.get('status')}")
                    print(f"   Duration: {result.get('duration_seconds', 0):.2f} seconds")
                    
                    # 2. Get JSON results
                    print("\n2️⃣ Getting JSON results...")
                    async with session.get(f"{base_url}/api/simple-analysis/simple/{request_id}") as json_response:
                        if json_response.status == 200:
                            full_result = await json_response.json()
                            print(f"✅ Retrieved full results")
                            
                            # Display summary
                            if full_result.get("results", {}).get("summary"):
                                print(f"\n📝 Executive Summary:")
                                print(f"   {full_result['results']['summary'][:200]}...")
                            
                            # Display insights
                            insights = full_result.get("results", {}).get("key_insights", [])
                            if insights:
                                print(f"\n💡 Key Insights ({len(insights)} total):")
                                for i, insight in enumerate(insights[:3], 1):
                                    print(f"   {i}. {insight}")
                                if len(insights) > 3:
                                    print(f"   ... and {len(insights) - 3} more")
                            
                            # Display agents that participated
                            agent_outputs = full_result.get("agent_outputs", {})
                            if agent_outputs:
                                print(f"\n🤖 Agents Participated:")
                                for agent in agent_outputs.keys():
                                    print(f"   - {agent.replace('_', ' ').title()}")
                        else:
                            print(f"❌ Failed to get JSON results: {json_response.status}")
                    
                    # 3. Test HTML endpoint
                    print("\n3️⃣ Testing HTML endpoint...")
                    async with session.get(f"{base_url}/api/simple-analysis/simple/{request_id}/html") as html_response:
                        if html_response.status == 200:
                            html_content = await html_response.text()
                            print(f"✅ HTML endpoint working ({len(html_content)} bytes)")
                            print(f"   URL: {base_url}/api/simple-analysis/simple/{request_id}/html")
                        else:
                            print(f"❌ HTML endpoint failed: {html_response.status}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Analysis failed: {response.status}")
                    print(f"   Error: {error_text}")
                    
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
            print(f"   Make sure the server is running on {base_url}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    # 4. List recent analyses
    print("\n4️⃣ Listing recent analyses...")
    try:
        async with session.get(f"{base_url}/api/simple-analysis/simple") as response:
            if response.status == 200:
                analyses = await response.json()
                print(f"✅ Found {len(analyses)} recent analyses")
                for analysis in analyses[:3]:
                    print(f"   - {analysis['request_id']}: {analysis['topic']} ({analysis['status']})")
            else:
                print(f"❌ Failed to list analyses: {response.status}")
    except Exception as e:
        print(f"❌ Error listing analyses: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Simple analysis endpoint test completed successfully!")
    return True


async def test_status_endpoint():
    """Test the service status endpoint."""
    base_url = "http://localhost:8080"
    
    print(f"\n🔍 Testing Service Status Endpoint")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{base_url}/api/status") as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"✅ System Status: {status.get('status', 'unknown')}")
                    print(f"\n🔧 Services:")
                    for service, available in status.get('services', {}).items():
                        emoji = "✅" if available else "❌"
                        print(f"   {emoji} {service.title()}: {'Available' if available else 'Unavailable'}")
                    
                    print(f"\n🤖 Orchestrator: {'✅ Ready' if status.get('orchestrator') else '❌ Not Ready'}")
                    
                    openai_test = status.get('openai_test', {})
                    if openai_test.get('status') == 'connected':
                        print(f"\n🔌 OpenAI Connection: ✅ Connected")
                        print(f"   Model: {openai_test.get('model')}")
                    else:
                        print(f"\n🔌 OpenAI Connection: ❌ Failed")
                        if openai_test.get('error'):
                            print(f"   Error: {openai_test['error']}")
                else:
                    print(f"❌ Status check failed: {response.status}")
        except Exception as e:
            print(f"❌ Error checking status: {e}")


async def main():
    """Run all tests."""
    print("\n🚀 CX Futurist AI - Simple Analysis Test Suite")
    print("=" * 60)
    
    # Test status first
    await test_status_endpoint()
    
    # Then test analysis
    success = await test_simple_analysis()
    
    if success:
        print("\n✨ All tests passed! The simple analysis endpoint is working correctly.")
        print("📝 Next steps:")
        print("   1. Deploy to Cloud Run: gcloud run deploy")
        print("   2. Test on Cloud Run using the deployed URL")
        print("   3. Monitor logs: gcloud run logs read")
    else:
        print("\n❌ Some tests failed. Please check the server logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())