"""Test production WebSocket endpoints."""

import asyncio
import websockets
import json
import ssl


async def test_websocket(url):
    """Test WebSocket connection to production."""
    # Create SSL context that doesn't verify certificates (for testing)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    print(f"🔌 Connecting to: {url}")
    
    try:
        async with websockets.connect(url, ssl=ssl_context) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for initial message
            initial_msg = await websocket.recv()
            data = json.loads(initial_msg)
            print(f"📥 Initial message: {data}")
            
            # Send ping
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print("📤 Sent ping")
            
            # Wait for pong
            pong_msg = await websocket.recv()
            pong_data = json.loads(pong_msg)
            print(f"📥 Received: {pong_data}")
            
            # Send subscription
            sub_msg = {"type": "subscribe", "channel": "agents"}
            await websocket.send(json.dumps(sub_msg))
            print("📤 Sent subscription")
            
            # Collect responses for 3 seconds
            end_time = asyncio.get_event_loop().time() + 3
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    data = json.loads(response)
                    print(f"📥 Received: {data.get('type', 'unknown')} - {data}")
                except asyncio.TimeoutError:
                    continue
                    
            print("✅ WebSocket test completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {type(e).__name__}: {e}")
        return False


async def main():
    """Test both WebSocket endpoints."""
    base_url = "https://cx-futurist-api-ws-4bgenndxea-uc.a.run.app"
    ws_base = base_url.replace("https://", "wss://")
    
    print("🧪 Testing CX Futurist AI Production WebSocket Endpoints")
    print("=" * 60)
    
    # Test /ws endpoint
    print("\n📍 Testing /ws endpoint...")
    ws_success = await test_websocket(f"{ws_base}/ws")
    
    # Test /simple-ws endpoint
    print("\n📍 Testing /simple-ws endpoint...")
    simple_ws_success = await test_websocket(f"{ws_base}/simple-ws")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   /ws endpoint: {'✅ PASSED' if ws_success else '❌ FAILED'}")
    print(f"   /simple-ws endpoint: {'✅ PASSED' if simple_ws_success else '❌ FAILED'}")
    print("=" * 60)
    
    return ws_success or simple_ws_success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)