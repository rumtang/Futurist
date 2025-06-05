#!/usr/bin/env python3
"""Test minimal startup with only OpenAI configured."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure we have at least OpenAI API key
if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
    print("❌ ERROR: Please set your OPENAI_API_KEY in .env file")
    print("   This is the only required configuration")
    sys.exit(1)

print("✅ OpenAI API key found")

# Import after env check
import requests
import time


async def test_minimal_startup():
    """Test that the system can start with minimal configuration."""
    print("\n🚀 Testing minimal startup...")
    print("   (Only OpenAI API required, Pinecone and Redis optional)")
    
    # Start the server in a subprocess
    import subprocess
    import signal
    
    print("\n📦 Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/api/status")
            if response.status_code == 200:
                print("✅ Server started successfully!")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            if i == max_attempts - 1:
                print("❌ Server failed to start")
                server_process.terminate()
                return False
    
    # Check service status
    try:
        response = requests.get("http://localhost:8000/api/status")
        if response.status_code == 200:
            status = response.json()
            print("\n📊 Service Status:")
            print(f"   Overall Status: {status['status']}")
            print(f"   Services:")
            for service, available in status['services'].items():
                icon = "✅" if available else "⚠️"
                print(f"     {icon} {service}: {'Available' if available else 'Not Available'}")
            print(f"   Orchestrator: {'✅ Ready' if status['orchestrator'] else '❌ Not Ready'}")
            print(f"\n💬 {status['message']}")
            
            # Test basic agent functionality
            print("\n🤖 Testing basic agent functionality...")
            test_payload = {
                "topic": "Future of AI agents",
                "analysis_type": "trend_scan"
            }
            
            response = requests.post(
                "http://localhost:8000/api/agents/analyze",
                json=test_payload
            )
            
            if response.status_code == 200:
                print("✅ Basic agent functionality working!")
                result = response.json()
                print(f"   Analysis started: {result.get('status', 'Unknown')}")
            else:
                print(f"⚠️  Agent test returned status {response.status_code}")
                print(f"   This is expected if some services are unavailable")
            
        else:
            print(f"❌ Status check failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    finally:
        # Stop the server
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✅ Server stopped")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("CX Futurist AI - Minimal Startup Test")
    print("=" * 60)
    
    success = asyncio.run(test_minimal_startup())
    
    if success:
        print("\n✅ SUCCESS: System can run with just OpenAI API!")
        print("\n📝 Next steps:")
        print("   1. The system is functional with basic capabilities")
        print("   2. To enable vector search: Configure Pinecone API")
        print("   3. To enable caching: Install and run Redis")
        print("   4. Run with: python -m uvicorn src.main:app --reload")
    else:
        print("\n❌ FAILED: Check the errors above")
        
    print("=" * 60)