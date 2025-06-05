"""Test WebSocket functionality locally before deployment."""

import asyncio
import websockets
import json
from datetime import datetime


async def test_websocket():
    """Test WebSocket connection and messages."""
    uri = "ws://localhost:8080/simple-ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")
            
            # Wait for connection message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📥 Received: {data['type']} - {data.get('message', '')}")
            
            # Test ping/pong
            print("\n🏓 Testing ping/pong...")
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data['type']}")
            
            # Test subscription
            print("\n📡 Testing subscription...")
            await websocket.send(json.dumps({
                "type": "subscribe",
                "channel": "agents"
            }))
            
            # Receive subscription confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data['type']} for channel: {data.get('channel', 'unknown')}")
            
            # Receive system state
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data['type']}")
            print(f"   Agents: {list(data.get('agents', {}).keys())}")
            print(f"   Services: {data.get('services', {})}")
            
            # Test analysis request
            print("\n🔬 Testing analysis request...")
            await websocket.send(json.dumps({
                "type": "request_analysis",
                "id": "test_analysis_123",
                "topic": "Future of AI Agents"
            }))
            
            # Collect responses for 5 seconds
            print("\n📊 Collecting analysis responses...")
            end_time = asyncio.get_event_loop().time() + 5
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    data = json.loads(response)
                    
                    if data['type'] == 'analysis:started':
                        print(f"🚀 Analysis started: {data.get('topic', '')}")
                    elif data['type'] == 'agent:status':
                        agent = data.get('agent', 'unknown')
                        status = data.get('data', {}).get('status', 'unknown')
                        print(f"🤖 {agent}: {status}")
                    elif data['type'] == 'agent:thought':
                        agent = data.get('agent', 'unknown')
                        thought = data.get('thought', {}).get('content', '')
                        print(f"💭 {agent}: {thought}")
                    elif data['type'] == 'analysis:completed':
                        print(f"✅ Analysis completed!")
                        results = data.get('results', {})
                        print(f"   Summary: {results.get('summary', '')}")
                        print(f"   Insights: {len(results.get('insights', []))} found")
                        break
                    
                except asyncio.TimeoutError:
                    continue
            
            print("\n✅ All WebSocket tests passed!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True


async def test_multiple_connections():
    """Test multiple concurrent WebSocket connections."""
    print("\n🔄 Testing multiple concurrent connections...")
    
    async def connect_and_ping(client_id):
        uri = "ws://localhost:8080/ws"
        try:
            async with websockets.connect(uri) as websocket:
                # Send ping
                await websocket.send(json.dumps({"type": "ping", "client_id": client_id}))
                # Wait for pong
                response = await websocket.recv()
                data = json.loads(response)
                if data['type'] == 'pong':
                    print(f"✅ Client {client_id} received pong")
                    return True
        except Exception as e:
            print(f"❌ Client {client_id} failed: {e}")
            return False
        return False
    
    # Connect 5 clients simultaneously
    tasks = [connect_and_ping(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(results)
    print(f"\n📊 {success_count}/5 clients connected successfully")
    
    return success_count == 5


async def main():
    """Run all WebSocket tests."""
    print("🧪 Starting WebSocket tests...\n")
    
    # Test basic functionality
    basic_test = await test_websocket()
    
    # Test multiple connections
    multi_test = await test_multiple_connections()
    
    # Summary
    print("\n" + "="*50)
    print("📋 Test Summary:")
    print(f"   Basic WebSocket: {'✅ PASSED' if basic_test else '❌ FAILED'}")
    print(f"   Multiple Connections: {'✅ PASSED' if multi_test else '❌ FAILED'}")
    print("="*50)
    
    return basic_test and multi_test


if __name__ == "__main__":
    # First, make sure the server is running:
    print("⚠️  Make sure the server is running with:")
    print("   python -m uvicorn src.main_production:app --reload --port 8080")
    print("")
    input("Press Enter when server is running...")
    
    # Run tests
    success = asyncio.run(main())
    exit(0 if success else 1)