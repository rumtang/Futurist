#!/usr/bin/env python3
"""Test WebSocket connection to deployed service."""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket(url):
    """Test WebSocket connection and messaging."""
    print(f"🔌 Connecting to: {url}")
    
    try:
        async with websockets.connect(url, ping_interval=20, ping_timeout=60) as websocket:
            print("✅ Connected successfully!")
            
            # Test 1: Initial connection message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Initial message: {data}")
            
            # Test 2: Subscribe
            subscribe_msg = {"type": "subscribe", "channel": "all"}
            await websocket.send(json.dumps(subscribe_msg))
            print(f"📤 Sent: {subscribe_msg}")
            
            # Wait for subscription confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📨 Subscription response: {data}")
            
            # Test 3: Ping-pong
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print(f"📤 Sent: {ping_msg}")
            
            # Wait for pong
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📨 Pong response: {data}")
            
            # Test 4: Custom message
            test_msg = {
                "type": "test",
                "message": "Hello from test script",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(test_msg))
            print(f"📤 Sent: {test_msg}")
            
            # Wait for echo
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📨 Echo response: {data}")
            
            print("\n✅ All tests passed!")
            
            # Keep connection open for a bit to test stability
            print("\n⏳ Testing connection stability for 5 seconds...")
            await asyncio.sleep(5)
            
            print("✅ Connection stable!")
            
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Use provided URL
        base_url = sys.argv[1]
    else:
        # Default to localhost
        base_url = "http://localhost:8080"
    
    # Convert HTTP to WebSocket URL
    ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
    
    # Add WebSocket endpoint
    if not ws_url.endswith("/simple-ws"):
        ws_url += "/simple-ws"
    
    print(f"🚀 WebSocket Test Script")
    print(f"📍 Base URL: {base_url}")
    print(f"🔌 WebSocket URL: {ws_url}")
    print("="*50)
    
    # Run test
    asyncio.run(test_websocket(ws_url))

if __name__ == "__main__":
    main()